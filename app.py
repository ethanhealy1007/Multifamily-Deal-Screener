"""Multifamily Deal Screener: a first-pass underwriting screen for multifamily deals."""

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Multifamily Deal Screener", page_icon="🏢", layout="wide")


# ---------------------------------------------------------------------------
# Calculations
# ---------------------------------------------------------------------------

def annual_debt_service(loan, rate, amort_years):
    """Annual principal + interest on a fully amortizing loan."""
    if loan <= 0:
        return 0.0
    monthly_rate = rate / 12
    months = amort_years * 12
    if monthly_rate == 0:
        return loan / months * 12
    monthly_payment = loan * monthly_rate / (1 - (1 + monthly_rate) ** -months)
    return monthly_payment * 12


def max_loan(price, noi, rate, amort_years, min_dscr, max_ltv):
    """Size the loan by LTV and by DSCR; the smaller one controls."""
    by_ltv = price * max_ltv
    # Debt service per $1 of loan ("loan constant") lets us solve for the DSCR loan
    loan_constant = annual_debt_service(1, rate, amort_years)
    by_dscr = noi / (min_dscr * loan_constant)
    if by_dscr < by_ltv:
        return by_dscr, by_ltv, by_dscr, "DSCR"
    return by_ltv, by_ltv, by_dscr, "LTV"


def money(value):
    """Format dollars, e.g. 4800000 -> $4,800,000."""
    return f"${value:,.0f}"


def safe(text):
    """Escape $ so Streamlit doesn't treat text between two $ signs as a math formula."""
    return text.replace("$", "\\$")


def dollar_input(label, default):
    """Text box for dollar amounts that accepts commas and $ signs (e.g. $4,800,000).

    Returns the amount as a number, or None (with an error message) if the entry is invalid.
    """
    text = st.text_input(label, value=f"{default:,}")
    cleaned = text.replace(",", "").replace("$", "").strip()
    try:
        amount = float(cleaned)
    except ValueError:
        st.error(safe(f"{label}: enter a number, for example {default:,}."))
        return None
    if amount < 0:
        st.error(safe(f"{label}: the amount can't be negative."))
        return None
    return amount


# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------

st.title("🏢 Multifamily Deal Screener")
st.write(
    "Run a fast first-pass underwriting screen on a multifamily acquisition. "
    "Enter the property and loan details below. The metrics, loan sizing, and "
    "pass/fail screen update automatically as you type."
)

# ---------------------------------------------------------------------------
# Sidebar: lender screening thresholds
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("Screening Thresholds")
    st.caption("Adjust to match the lender or program you are screening against.")
    min_dscr = st.slider("Minimum DSCR", 1.00, 1.60, 1.25, step=0.05, format="%.2fx")
    max_ltv_pct = st.slider("Maximum LTV", 50, 85, 80, step=1, format="%d%%")
    min_debt_yield_pct = st.slider("Minimum debt yield", 5.0, 12.0, 8.0, step=0.5, format="%.1f%%")

max_ltv = max_ltv_pct / 100
min_debt_yield = min_debt_yield_pct / 100

# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------

property_col, loan_col = st.columns(2)

with property_col:
    st.subheader("Property")
    name = st.text_input("Property name", value="Sample Garden Apartments")
    units = st.number_input("Number of units", min_value=1, value=24, step=1)
    price = dollar_input("Purchase price ($)", 4_800_000)
    noi = dollar_input("Net operating income, annual ($)", 312_000)

with loan_col:
    st.subheader("Proposed Loan")
    loan = dollar_input("Requested loan amount ($)", 3_600_000)
    rate_pct = st.number_input("Interest rate (%)", min_value=0.0, max_value=20.0,
                               value=6.25, step=0.125, format="%.3f")
    amort_years = st.selectbox("Amortization (years)", [25, 30, 35], index=1)

rate = rate_pct / 100

if price is None or noi is None or loan is None:
    st.stop()  # an error message is already shown under the bad entry
if price <= 0 or noi <= 0 or loan <= 0:
    st.warning("Enter a purchase price, NOI, and loan amount greater than $0 to run the screen.")
    st.stop()

# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------

debt_service = annual_debt_service(loan, rate, amort_years)
cap_rate = noi / price
ltv = loan / price
dscr = noi / debt_service
debt_yield = noi / loan
price_per_unit = price / units
sized_loan, ltv_loan, dscr_loan, controlling = max_loan(
    price, noi, rate, amort_years, min_dscr, max_ltv)

st.divider()
st.header(f"Results: {name or 'Unnamed property'}")

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Cap rate", f"{cap_rate:.2%}")
m2.metric("Price / unit", money(price_per_unit))
m3.metric("LTV", f"{ltv:.1%}")
m4.metric("DSCR", f"{dscr:.2f}x")
m5.metric("Debt yield", f"{debt_yield:.2%}")
m6.metric("Annual debt service", money(debt_service))

# --- Pass/fail screen -------------------------------------------------------
checks = [
    ("DSCR", f"{dscr:.2f}x", f"≥ {min_dscr:.2f}x", dscr >= min_dscr),
    ("LTV", f"{ltv:.1%}", f"≤ {max_ltv:.0%}", ltv <= max_ltv),
    ("Debt yield", f"{debt_yield:.2%}", f"≥ {min_debt_yield:.1%}", debt_yield >= min_debt_yield),
]
screen_table = pd.DataFrame(
    [{"Metric": m, "Deal": v, "Threshold": t, "Result": "✅ Pass" if ok else "❌ Fail"}
     for m, v, t, ok in checks]
)
failed = [m for m, _, _, ok in checks if not ok]

screen_col, sizing_col = st.columns(2)

with screen_col:
    st.subheader("Screening")
    st.dataframe(screen_table, hide_index=True)

with sizing_col:
    st.subheader("Loan Sizing")
    st.dataframe(
        pd.DataFrame([
            {"Constraint": f"Max LTV ({max_ltv:.0%})", "Max loan": money(ltv_loan)},
            {"Constraint": f"Min DSCR ({min_dscr:.2f}x)", "Max loan": money(dscr_loan)},
        ]),
        hide_index=True,
    )
    st.write(safe(f"**Maximum supportable loan: {money(sized_loan)}** ({controlling}-constrained)"))

# --- Recommendation ---------------------------------------------------------
if not failed:
    st.success(safe(f"Passes all screens. The requested {money(loan)} loan fits within the "
                    f"{money(sized_loan)} maximum. Proceed to full underwriting."))
else:
    gap = loan - sized_loan
    message = f"Fails: {', '.join(failed)}. "
    if gap > 0:
        message += (f"The requested loan is {money(gap)} above the {money(sized_loan)} "
                    f"maximum ({controlling}-constrained). Consider resizing the loan.")
    else:
        message += "Review the failing metrics before moving to full underwriting."
    st.error(safe(message))

# --- Rate sensitivity chart -------------------------------------------------
st.subheader("DSCR Sensitivity to Interest Rate")
st.caption("How DSCR on the requested loan changes if the rate moves. "
           "Points below the minimum DSCR line fail the screen.")
rates = [round(rate_pct + step * 0.25, 3) for step in range(-8, 9) if rate_pct + step * 0.25 > 0]
sensitivity = pd.DataFrame({
    "Interest rate (%)": rates,
    "DSCR": [noi / annual_debt_service(loan, r / 100, amort_years) for r in rates],
    "Minimum DSCR": [min_dscr] * len(rates),
})
st.line_chart(sensitivity, x="Interest rate (%)", y=["DSCR", "Minimum DSCR"])