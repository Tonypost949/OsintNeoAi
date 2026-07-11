"""
Social media collector for OSINT Independent Platform.
Handles Twitter, LinkedIn, Facebook, Instagram, Reddit, etc.
"""
import asyncio
import re
from typing import Any, Dict, List, Optional

import aiohttp

from .base import BaseCollector, CollectorResult, collector
from ..core.models import Entity, EntityType, Observation, Source, SourceType, ConfidenceLevel


@collector(
    name="twitter",
    description="Twitter/X intelligence",
    supported_types=[EntityType.PERSON, EntityType.EMAIL, EntityType.DOMAIN],
    rate_limit=300,
    timeout=30
)
class TwitterCollector(BaseCollector):
    """Twitter/X API integration (v2)."""
    
    BASE_URL = "https://api.twitter.com/2"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.bearer_token = self.collectors.api_keys.get('twitter_bearer', '')
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            headers = {'Authorization': f'Bearer {self.bearer_token}'} if self.bearer_token else {}
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self.session
    
    async def collect(self, target: str, **kwargs) -> CollectorResult:
        if not self.bearer_token:
            return CollectorResult(errors=["Twitter Bearer token not configured"])
        
        await self._wait_for_rate_limit()
        job = self._start_job(target, kwargs)
        result = CollectorResult()
        
        try:
            if self._is_username(target):
                await self._collect_user(target, result)
            elif self._is_email(target):
                await self._search_email(target, result)
        except Exception as e:
            result.errors.append(str(e))
        finally:
            self._complete_job(result)
        
        return result
    
    async def _collect_user(self, username: str, result: CollectorResult) -> None:
        session = await self._get_session()
        
        # Get user by username
        url = f"{self.BASE_URL}/users/by/username/{username}"
        params = {'user.fields': 'id,name,username,created_at,description,location,url,public_metrics,verified,profile_image_url'}
        
        async with session.get(url, params=params) as resp:
            if resp.status == 404:
                return
            data = await resp.json()
        
        user = data.get('data', {})
        
        user_entity = self._create_entity(
            EntityType.PERSON, f"@{username}",
            name=user.get('name', ''),
            source_name="twitter",
            source_type=SourceType.SOCIAL,
            attributes={
                'twitter_id': user.get('id'),
                'username': username,
                'description': user.get('description'),
                'location': user.get('location'),
                'url': user.get('url'),
                'verified': user.get('verified', False),
                'followers': user.get('public_metrics', {}).get('followers_count', 0),
                'following': user.get('public_metrics', {}).get('following_count', 0),
                'tweets': user.get('public_metrics', {}).get('tweet_count', 0),
                'created_at': user.get('created_at')
            }
        )
        result.entities.append(user_entity)
        
        # Get recent tweets
        tweets_url = f"{self.BASE_URL}/users/{user.get('id')}/tweets"
        params = {'max_results': 100, 'tweet.fields': 'created_at,public_metrics,entities,context_annotations'}
        
        async with session.get(tweets_url, params=params) as resp:
            if resp.status == 200:
                tweets_data = await resp.json()
                for tweet in tweets_data.get('data', []):
                    obs = self._create_observation(user_entity.id, {
                        'type': 'twitter_tweet',
                        'tweet_id': tweet.get('id'),
                        'text': tweet.get('text'),
                        'created_at': tweet.get('created_at'),
                        'metrics': tweet.get('public_metrics', {}),
                        'entities': tweet.get('entities', {}),
                        'context': tweet.get('context_annotations', [])
                    })
                    result.observations.append(obs)
    
    async def _search_email(self, email: str, result: CollectorResult) -> None:
        # Twitter doesn't allow email search via API
        pass
    
    def _is_username(self, target: str) -> bool:
        return target.startswith('@') or re.match(r'^[A-Za-z0-9_]{1,15}$', target) is not None
    
    def _is_email(self, target: str) -> bool:
        return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', target) is not None


@collector(
    name="reddit",
    description="Reddit intelligence",
    supported_types=[EntityType.PERSON, EntityType.DOMAIN, EntityType.EMAIL],
    rate_limit=60,
    timeout=30
)
class RedditCollector(BaseCollector):
    """Reddit API integration."""
    
    BASE_URL = "https://www.reddit.com"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.client_id = self.collectors.api_keys.get('reddit_client_id', '')
        self.client_secret = self.collectors.api_keys.get('reddit_client_secret', '')
        self.user_agent = "OSINT-Independent/1.0"
        self.session: Optional[aiohttp.ClientSession] = None
        self._access_token: Optional[str] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            headers = {'User-Agent': self.user_agent}
            if self._access_token:
                headers['Authorization'] = f'Bearer {self._access_token}'
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self.session
    
    async def _authenticate(self) -> None:
        if not self.client_id or not self.client_secret:
            return
        
        session = await self._get_session()
        auth = aiohttp.BasicAuth(self.client_id, self.client_secret)
        data = {'grant_type': 'client_credentials'}
        
        async with session.post('https://www.reddit.com/api/v1/access_token', 
                                auth=auth, data=data) as resp:
            if resp.status == 200:
                data = await resp.json()
                self._access_token = data.get('access_token')
                self.session.headers['Authorization'] = f'Bearer {self._access_token}'
    
    async def collect(self, target: str, **kwargs) -> CollectorResult:
        await self._wait_for_rate_limit()
        
        if self.client_id and self.client_secret and not self._access_token:
            await self._authenticate()
        
        job = self._start_job(target, kwargs)
        result = CollectorResult()
        
        try:
            if self._is_username(target):
                await self._collect_user(target, result)
            elif self._is_subreddit(target):
                await self._collect_subreddit(target, result)
        except Exception as e:
            result.errors.append(str(e))
        finally:
            self._complete_job(result)
        
        return result
    
    async def _collect_user(self, username: str, result: CollectorResult) -> None:
        session = await self._get_session()
        url = f"{self.BASE_URL}/user/{username}/about.json"
        
        async with session.get(url) as resp:
            if resp.status == 404:
                return
            data = await resp.json()
        
        user = data.get('data', {})
        
        user_entity = self._create_entity(
            EntityType.PERSON, f"u/{username}",
            name=user.get('name', ''),
            source_name="reddit",
            source_type=SourceType.SOCIAL,
            attributes={
                'reddit_id': user.get('id'),
                'username': username,
                'created_utc': user.get('created_utc'),
                'comment_karma': user.get('comment_karma'),
                'link_karma': user.get('link_karma'),
                'is_mod': user.get('is_mod', False),
                'is_gold': user.get('is_gold', False)
            }
        )
        result.entities.append(user_entity)
        
        # Get user submissions
        submissions_url = f"{self.BASE_URL}/user/{username}/submitted.json"
        async with session.get(submissions_url, params={'limit': 100}) as resp:
            if resp.status == 200:
                data = await resp.json()
                for post in data.get('data', {}).get('children', []):
                    post_data = post.get('data', {})
                    obs = self._create_observation(user_entity.id, {
                        'type': 'reddit_post',
                        'post_id': post_data.get('id'),
                        'title': post_data.get('title'),
                        'subreddit': post_data.get('subreddit'),
                        'score': post_data.get('score'),
                        'created_utc': post_data.get('created_utc'),
                        'url': post_data.get('url'),
                        'selftext': post_data.get('selftext', '')[:500]
                    })
                    result.observations.append(obs)
    
    async def _collect_subreddit(self, subreddit: str, result: CollectorResult) -> None:
        session = await self._get_session()
        url = f"{self.BASE_URL}/r/{subreddit}/about.json"
        
        async with session.get(url) as resp:
            if resp.status == 404:
                return
            data = await resp.json()
        
        sub = data.get('data', {})
        
        sub_entity = self._create_entity(
            EntityType.ORGANIZATION, f"r/{subreddit}",
            name=sub.get('title', ''),
            source_name="reddit",
            source_type=SourceType.SOCIAL,
            attributes={
                'subreddit': subreddit,
                'subscribers': sub.get('subscribers'),
                'description': sub.get('public_description'),
                'created_utc': sub.get('created_utc'),
                'over18': sub.get('over18', False)
            }
        )
        result.entities.append(sub_entity)
    
    def _is_username(self, target: str) -> bool:
        return target.startswith('u/') or re.match(r'^[A-Za-z0-9_-]{3,20}$', target) is not None
    
    def _is_subreddit(self, target: str) -> bool:
        return target.startswith('r/') or re.match(r'^[A-Za-z0-9_]{3,21}$', target) is not None


@collector(
    name="linkedin",
    description="LinkedIn professional intelligence",
    supported_types=[EntityType.PERSON, EntityType.ORGANIZATION],
    rate_limit=10,
    timeout=30
)
class LinkedInCollector(BaseCollector):
    """LinkedIn intelligence (limited to public data)."""
    
    BASE_URL = "https://www.linkedin.com"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={'User-Agent': self.collector_config.user_agent},
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self.session
    
    async def collect(self, target: str, **kwargs) -> CollectorResult:
        await self._wait_for_rate_limit()
        job = self._start_job(target, kwargs)
        result = CollectorResult()
        
        try:
            # LinkedIn requires auth for most data, limited to public profile scraping
            if self._is_profile_url(target):
                await self._collect_profile(target, result)
        except Exception as e:
            result.errors.append(str(e))
        finally:
            self._complete_job(result)
        
        return result
    
    async def _collect_profile(self, url: str, result: CollectorResult) -> None:
        session = await self._get_session()
        
        # Note: LinkedIn heavily blocks scraping. This is a placeholder for public data only.
        # In practice, you'd need LinkedIn API partnership or use a service like Proxycurl
        try:
            async with session.get(url) as resp:
                html = await resp.text()
                # Parse public profile data from HTML
                # This is very limited due to LinkedIn's anti-scraping
        except Exception:
            pass
    
    def _is_profile_url(self, target: str) -> bool:
        return 'linkedin.com/in/' in target or 'linkedin.com/company/' in target


@collector(
    name="social",
    description="Multi-platform social media search",
    supported_types=[EntityType.PERSON, EntityType.EMAIL, EntityType.DOMAIN, EntityType.PHONE],
    rate_limit=10,
    timeout=30
)
class SocialCollector(BaseCollector):
    """Search across multiple social platforms using search engines."""
    
    PLATFORMS = {
        'twitter': 'site:twitter.com',
        'linkedin': 'site:linkedin.com',
        'facebook': 'site:facebook.com',
        'instagram': 'site:instagram.com',
        'github': 'site:github.com',
        'reddit': 'site:reddit.com',
        'youtube': 'site:youtube.com',
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={'User-Agent': self.collector_config.user_agent},
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self.session
    
    async def collect(self, target: str, **kwargs) -> CollectorResult:
        await self._wait_for_rate_limit()
        job = self._start_job(target, kwargs)
        result = CollectorResult()
        
        try:
            session = await self._get_session()
            
            for platform, dork in self.PLATFORMS.items():
                query = f"{dork} \"{target}\""
                # Use duckduckgo html scraping or similar
                # This is a placeholder - real implementation would use a search API
                
        except Exception as e:
            result.errors.append(str(e))
        finally:
            self._complete_job(result)
        
        return result