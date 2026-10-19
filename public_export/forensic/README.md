# NPI Calculator

**Non-Profiteers Index** — Forensic analysis tool for identifying fraudulent nonprofits using financial ratio analysis.

## What is the NPI?

The NPI is a quantitative methodology for detecting nonprofits that function as government contractors or exist primarily for institutional self-preservation rather than mission delivery. It uses a simple formula based on financial filing data:

```
NPI = (Asset Accumulation Ratio) × (Overhead Distortion Ratio)
```

### Risk Classification
- **Low Risk** (NPI < 0.5): Healthy nonprofit structure
- **Moderate Risk** (0.5–2.0): Notable concerns, investigate further
- **High Risk** (2.0–5.0): Significant fraud indicators
- **Critical Risk** (NPI > 5.0): Extremely suspicious pattern

## Red Flags

The calculator automatically identifies:
- **Government dependency >80%** — org functions as federal contractor
- **Asset accumulation >1 year of income** — capital preservation vs. mission
- **Direct services <15%** — overhead-heavy structure
- **Consecutive audit findings** — regulatory non-compliance

## How to Use

1. Enter organizational financials from Form 990 Part IX
2. Click "Calculate NPI" to generate the forensic score
3. Review flagged indicators and risk classification
4. Use results to prioritize investigation resources

### Test Data

Click "Load Viet America Society" to see a real example from the Andrew Do/Peter Pham nonprofit fraud case (Orange County, 2022).

## Deployment

### Option 1: Vercel (Easiest - Recommended)

1. **Create GitHub account** (free): https://github.com/signup
2. **Create new repository** (click + icon, select "New repository")
   - Name: `npi-calculator`
   - Description: `Non-Profiteers Index forensic calculator`
   - Public
   - Add `README.md` (optional)
3. **Upload files**: Clone repo locally, copy `index.html` into it, push to GitHub
4. **Deploy to Vercel**:
   - Go to https://vercel.com/new
   - Click "Import Git Repository"
   - Select your `npi-calculator` repo
   - Click Deploy (takes 30 seconds)
   - Get live URL instantly

### Option 2: Netlify

1. Go to https://netlify.com
2. Sign up with GitHub
3. Click "New site from Git"
4. Select your `npi-calculator` repo
5. Auto-deploys when you push changes

### Option 3: GitHub Pages (Free)

1. Enable GitHub Pages in repo settings
2. Select main branch as source
3. Get live at `yourname.github.io/npi-calculator`

## Files

- `index.html` — Complete standalone app (no dependencies)
- No build step required — just upload and serve

## License

Built for nonprofit forensic analysis and research.

## Questions?

Review your NPI methodology documentation for the complete statistical framework and validation data.
