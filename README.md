# Where Google Merch Store Shoppers Drop Off: GA4 Funnel Analysis in BigQuery

![tests](https://github.com/YOUR_USERNAME/ga4-funnel-analysis/actions/workflows/tests.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.12-blue) ![BigQuery](https://img.shields.io/badge/SQL-BigQuery-4285F4)

**TL;DR**
- Modeled **4.3M events from 270K users** (360K sessions, Nov 2020 – Jan 2021) of Google Merchandise Store GA4 data in BigQuery.
- Biggest leak: **product view → add to cart**, where **80% of sessions drop off**. **Paid Search** converts **14.1 pts worse than Organic Search** at cart → checkout (23.2% vs 37.3%; 95% CI −19.1 to −9.1, significant after FDR correction).
- Closing half of the Paid Search gap to the overall rate would add about **7 orders (~$460) per quarter** in this sample (range $230–$925).
- Contrary to the usual assumption, **mobile converts as well as desktop** and there's no significant device gap at any step.

