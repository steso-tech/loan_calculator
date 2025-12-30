import streamlit as st
import pandas as pd
import math

# Set page configuration
st.set_page_config(page_title="Loan Amortization Calculator", layout="wide")

st.title("💶 Loan Amortization Calculator")
st.markdown("Calculate your monthly payments, total interest, and see how **yearly extra payments** impact your loan term.")

# --- Input Section ---
with st.sidebar:
    st.header("Loan Details")
    loan_amount = st.number_input("Loan Amount (€)", min_value=1000.0, value=10000.0, step=500.0)
    annual_interest_rate = st.number_input("Annual Interest Rate (%)", min_value=0.1, value=5.0, step=0.1)
    period_months = st.number_input("Loan Period (Months)", min_value=1, value=60, step=1)
    
    st.header("Extra Payments")
    yearly_extra_payment_percent = st.number_input(
        "Yearly Extra Payment (% of Loan Amount)", 
        min_value=0.0, 
        max_value=100.0, 
        value=0.0, 
        step=0.1,
        help="This amount will be paid once a year (every 12th month) directly towards the principal."
    )

    calculate_btn = st.button("Calculate Loan", type="primary")

# --- Calculation Logic ---
if calculate_btn:
    # 1. Basic Calculations
    monthly_rate = (annual_interest_rate / 100) / 12
    
    # Calculate standard monthly payment (PMT formula)
    if monthly_rate > 0:
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** period_months) / ((1 + monthly_rate) ** period_months - 1)
    else:
        monthly_payment = loan_amount / period_months

    extra_payment_amount = loan_amount * (yearly_extra_payment_percent / 100)

    # 2. Amortization Schedule Loop
    balance = loan_amount
    schedule_data = []
    total_interest = 0
    months_count = 0

    # Iterate until balance is cleared or we hit a safety limit
    for month in range(1, period_months + 1200):  
        months_count += 1
        
        # Interest for this month
        interest = balance * monthly_rate
        total_interest += interest
        
        # Principal for this month
        principal_payment = monthly_payment - interest
        
        # Check if this is the final payment (balance < calculated principal)
        if balance < principal_payment:
            principal_payment = balance
            monthly_payment = interest + principal_payment # Adjust payment for last month
        
        balance -= principal_payment

        # Yearly Extra Payment Logic
        # Applied only if it's the 12th, 24th, 36th... month and balance > 0
        actual_extra_payment = 0
        if month % 12 == 0 and extra_payment_amount > 0 and balance > 0:
            if balance < extra_payment_amount:
                actual_extra_payment = balance
                balance = 0
            else:
                actual_extra_payment = extra_payment_amount
                balance -= actual_extra_payment
        
        # Store row data
        schedule_data.append({
            "Month": month,
            "Monthly Payment": monthly_payment,
            "Principal": principal_payment,
            "Interest": interest,
            "Yearly Extra Payment": actual_extra_payment,
            "Remaining Balance": balance
        })

        if balance <= 0:
            break

    # Create DataFrame
    df = pd.DataFrame(schedule_data)
    df_display = df.round(2)

    # --- Summary Section ---
    st.divider()
    st.subheader("📊 Loan Summary")
    
    col1, col2, col3 = st.columns(3)
    
    # Calculate years and months saved
    original_years = period_months / 12
    actual_years = months_count / 12
    years_saved = original_years - actual_years
    if years_saved < 0: years_saved = 0 # Prevent negative numbers if rounding errors occur

    # Format time to repay string
    years_repaid = math.floor(months_count / 12)
    months_repaid = months_count % 12
    time_repaid_str = f"{years_repaid} Years, {months_repaid} Months"

    with col1:
        st.metric("Total Interest Paid", f"€{total_interest:,.2f}")
    with col2:
        st.metric("Time to Repay", time_repaid_str)
    with col3:
        # Changed: Always show Time Saved, removed Monthly Payment display
        st.metric("Time Saved", f"{years_saved:.1f} Years")

    # --- Table & Export Section ---
    st.divider()
    st.subheader("📅 Amortization Schedule")
    
    # Export Button
    csv = df_display.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Schedule as CSV",
        data=csv,
        file_name='amortization_schedule.csv',
        mime='text/csv',
    )

    # Display Table with formatting
    st.dataframe(
        df_display.style.format({
            "Monthly Payment": "€{:.2f}",
            "Principal": "€{:.2f}",
            "Interest": "€{:.2f}",
            "Yearly Extra Payment": "€{:.2f}",
            "Remaining Balance": "€{:.2f}"
        }),
        use_container_width=True,
        height=500
    )

else:
    st.info("👈 Enter loan details in the sidebar and click **Calculate Loan** to see the results.")