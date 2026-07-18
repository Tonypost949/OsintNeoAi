# Graph Extraction Walkthrough

We have successfully processed the three target OSINT CSV datasets and transformed them into standard graph network data structures.

## Processing Summary

- **Total Unique Nodes**: 12,017
- **Total Edges**: 12,241

### Node Breakdown
- **ORGANIZATION / PERSON**: Identified and classified using company suffixes (LLC, INC, etc.)
- **PROPERTY**: Extracted from parcel identifiers (APNs) and physical locations.
- **ADDRESS**: Registered mailing coordinates.
- **STATE**: State boundary classifications.
- **PPP_LOAN**: PPP financial attributes (amount, count, forgiven sum).

### Edge Breakdown
- **OWNS**: Entity-to-property relationships.
- **REGISTERED_AT**: Entity-to-mailing address relationships.
- **RECEIVED_PPP**: Entity-to-loan relationships.
- **LOCATED_IN**: CoC-to-state or property-to-state relationships.
- **CONNECTED_TO**: Transaction connections from previous owners to current owners.

## Example Relationships
1. `OWNS`: `STEWART INDUSTRIES LLC` -> Property `178-431-14`
2. `REGISTERED_AT`: `STEWART INDUSTRIES LLC` -> Address `1077 PACIFIC COAST HWY # 247`
3. `RECEIVED_PPP`: `STEWART INDUSTRIES LLC` -> PPP Loan `loan_STEWART INDUSTRIES LLC`
4. `LOCATED_IN`: `Cincinnati/Hamilton County CoC` -> State `OH`
