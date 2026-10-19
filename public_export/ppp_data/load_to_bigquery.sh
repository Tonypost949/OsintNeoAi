#!/bin/bash
# Load PPP 11770 W*** Ave data into BigQuery
# Prerequisites: gcloud auth login (already authenticated)

bq load \
  --source_format=NEWLINE_DELIMITED_JSON \
  --autodetect \
  noble-beanbag-497411-m4:ppp_rico.ppp_117**_warner \
  ppp_117**_warner_bq.json \
  ppp_bq_schema.json
