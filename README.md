# Multifamily Deal Screener

## Student Name
Ethan Healy

## App Description
The Multifamily Deal Screener is a Streamlit app for running a fast first-pass underwriting screen on a multifamily acquisition. Users enter a property's units, purchase price, and net operating income along with the proposed loan amount, interest rate, and amortization. The app instantly calculates core underwriting metrics, sizes the maximum loan the property can support under DSCR and LTV constraints, and tells the user whether the deal passes lender screening thresholds, which can be adjusted in the sidebar to match different lenders or loan programs.

## Intended Users
This app is intended for commercial real estate analysts, loan originators, and finance students who need a fast first-pass screen of multifamily acquisitions or refinances before building a full underwriting model.

## How to Run
```
pip install -r requirements.txt
streamlit run app.py
```

## Current Features (Implemented)
- **Deal input form:** property name, number of units, purchase price, annual NOI, requested loan amount, interest rate, and amortization (25/30/35 years)
- **Adjustable screening thresholds:** sidebar sliders for minimum DSCR, maximum LTV, and minimum debt yield
- **Underwriting metrics:** cap rate, price per unit, LTV, DSCR, debt yield, and annual debt service, all updating automatically as inputs change
- **Loan sizing:** maximum loan under the LTV limit and under the DSCR minimum, with the smaller (controlling) constraint identified
- **Pass/fail screening table:** each metric compared against its threshold
- **Recommendation:** a green "proceed" message or a red message listing failed metrics and how far the requested loan is above the maximum
- **DSCR sensitivity chart:** shows how DSCR changes if the interest rate moves up or down, plotted against the minimum DSCR line
- - **Easy-to-read dollar inputs:** dollar amounts accept commas and $ signs (e.g. 4,800,000), with error messages for invalid entries

## Planned Features (Final Version)
- **Saved deal pipeline:** save screened deals to a Supabase database
- **Deal comparison:** view saved deals side by side in a sortable table
- **Interest-only option:** screen loans with an initial interest-only period
- **Expense and income inputs:** build NOI from gross rents, vacancy, and operating expenses instead of entering NOI directly
- **Deployment:** publish the app on Streamlit Community Cloud
