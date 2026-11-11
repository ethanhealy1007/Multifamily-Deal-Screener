# Multifamily Deal Screener

## Student Name
Ethan Healy

## App Description
The Multifamily Deal Screener is a Streamlit app that helps users quickly evaluate whether a multifamily property is worth a deeper underwriting review. Users enter a property's key value metrics (purchase price, net operating income, unit count, and proposed loan terms) and the app calculates core underwriting metrics such as cap rate, debt service coverage ratio (DSCR), loan-to-value (LTV), and debt yield. It also sizes the maximum supportable loan using DSCR and LTV constraints and flags whether the deal passes common lender screening thresholds. Screened deals can be saved and compared side by side.

## Intended Users
This app is intended for commercial real estate analysts, loan originators, and finance students who need a fast first-pass screen of multifamily acquisitions or refinances before building a full underwriting model.

## Planned Features
- **Deal input form:** enter property name, location, units, purchase price, NOI, interest rate, amortization, and requested loan amount
- **Underwriting metrics:** automatically calculate cap rate, price per unit, LTV, DSCR, debt yield, and annual debt service
- **Loan sizing:** calculate the maximum loan supported by a minimum DSCR and a maximum LTV, and show which constraint controls
- **Pass/fail screening:** flag each metric against adjustable thresholds (for example, DSCR ≥ 1.25x and LTV ≤ 80%)
- **Saved deal pipeline:** save screened deals to a database and compare them in a sortable table