import React from 'react';
import { APIProvider, Map, AdvancedMarker, Pin } from '@vis.gl/react-google-maps';
import { DOSSIER_DATA } from '../data/dossier';

const GOOGLE_MAPS_API_KEY = process.env.GOOGLE_MAPS_PLATFORM_KEY || '';

export const MapTracker: React.FC = () => {
  const locations = DOSSIER_DATA.entities.filter(e => e.location);

  if (!GOOGLE_MAPS_API_KEY) {
    return (
      <div className="w-full h-full flex flex-col items-center justify-center bg-zinc-900 border border-white/10 rounded-lg p-8 text-center">
        <h2 className="text-xl font-bold text-white mb-4">MAP INTERFACE OFFLINE</h2>
        <p className="text-zinc-400 max-w-md">
          Google Maps API Key is required for geospatial tracking. Please configure GOOGLE_MAPS_PLATFORM_KEY in your secrets.
        </p>
      </div>
    );
  }

  return (
    <div className="w-full h-full border border-white/10 rounded-lg overflow-hidden">
      <APIProvider apiKey={GOOGLE_MAPS_API_KEY}>
        <Map
          defaultCenter={{ lat: 33.0, lng: -117.5 }}
          defaultZoom={7}
          mapId="INVESTIGATION_TRACKER"
          style={{ width: '100%', height: '100%' }}
          gestureHandling={'greedy'}
          disableDefaultUI={false}
          styles={[
            {
              "elementType": "geometry",
              "stylers": [{ "color": "#212121" }]
            },
            {
              "elementType": "labels.icon",
              "stylers": [{ "visibility": "off" }]
            },
            {
              "elementType": "labels.text.fill",
              "stylers": [{ "color": "#757575" }]
            },
            {
              "elementType": "labels.text.stroke",
              "stylers": [{ "color": "#212121" }]
            },
            {
              "featureType": "administrative",
              "elementType": "geometry",
              "stylers": [{ "color": "#757575" }]
            },
            {
              "featureType": "water",
              "elementType": "geometry",
              "stylers": [{ "color": "#000000" }]
            }
          ]}
        >
          {locations.map(loc => (
            <AdvancedMarker
              key={loc.id}
              position={loc.location!}
              title={loc.name}
            >
              <Pin
                background={loc.id === 'tijuana' ? '#ef4444' : '#3b82f6'}
                glyphColor={'#fff'}
                borderColor={'#fff'}
              />
            </AdvancedMarker>
          ))}
        </Map>
      </APIProvider>
    </div>
  );
};
