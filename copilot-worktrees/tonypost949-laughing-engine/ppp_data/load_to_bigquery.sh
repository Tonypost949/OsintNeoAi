#!/bin/bash
# Load PPP 11770 Warner Ave data into BigQuery
# Prerequisites: gcloud auth login (already authenticated)

bq load \
  --source_format=NEWLINE_DELIMITED_JSON \
  --autodetect \
  noble-beanbag-497411-m4:ppp_rico.ppp_11770_warner \
  ppp_11770_warner_bq.json \
  ppp_bq_schema.json
