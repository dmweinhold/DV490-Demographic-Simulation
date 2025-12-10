import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Demographic Sim", layout="centered")

st.title("DV490 Demographic Simulation")
st.write("Adjust the parameters in the sidebar to see how population and dependency change over 300 years.")

# --- SIDEBAR INPUTS ---
st.sidebar.header("Input Parameters")

start_dist_type = st.sidebar.selectbox(
    "Starting Population Structure",
    ('Young (Developing)', 'Balanced (Stable)', 'Old (Shrinking)')
)

tfr = st.sidebar.slider("Fertility Rate (TFR)", 0.5, 6.0, 2.4, 0.1)
avg_birth_age = st.sidebar.slider("Avg Age at Birth", 18, 40, 28, 1)
retire_age = st.sidebar.slider("Retirement Age", 50, 80, 65, 1)
life_expectancy = st.sidebar.slider("Life Expectancy", 50, 100, 75, 1)


# --- SIMULATION LOGIC ---
def run_simulation(start_dist_type, tfr, avg_birth_age, retire_age, life_expectancy):
    years_to_project = 300
    work_start_age = 15
    max_age_limit = 120

    # Fertility Bell Curve
    reproductive_ages = np.arange(15, 50)
    std_dev = 5.0
    fertility_profile = np.exp(-((reproductive_ages - avg_birth_age) ** 2) / (2 * std_dev ** 2))
    if np.sum(fertility_profile) > 0:
        fertility_profile = fertility_profile / np.sum(fertility_profile) * tfr

    # Init Population
    pop_by_age = np.zeros(max_age_limit)
    initial_pop_size = 10000

    if start_dist_type == 'Young (Developing)':
        ages = np.arange(life_expectancy)
        pop_by_age[:life_expectancy] = np.exp(-0.04 * ages)
    elif start_dist_type == 'Balanced (Stable)':
        pop_by_age[:life_expectancy] = 1
    elif start_dist_type == 'Old (Shrinking)':
        ages = np.arange(life_expectancy)
        pop_by_age[:life_expectancy] = np.exp(0.015 * ages)

    pop_by_age = pop_by_age / np.sum(pop_by_age) * initial_pop_size

    history_years = []
    history_total_pop = []
    history_dep_ratio = []

    for year in range(years_to_project):
        total_pop = np.sum(pop_by_age)

        # Ranges
        young_pop = np.sum(pop_by_age[0:min(work_start_age, max_age_limit)])
        if retire_age > work_start_age:
            working_pop = np.sum(pop_by_age[work_start_age:min(retire_age, max_age_limit)])
        else:
            working_pop = 0
        old_pop = np.sum(pop_by_age[min(retire_age, max_age_limit):])

        if working_pop > 1:
            dep_ratio = (young_pop + old_pop) / working_pop * 100
        else:
            dep_ratio = 0

        history_years.append(year)
        history_total_pop.append(total_pop)
        history_dep_ratio.append(dep_ratio)

        # Births & Aging
        women_in_repro_age = pop_by_age[15:50] * 0.5
        new_babies = np.sum(women_in_repro_age * fertility_profile)
        pop_by_age[1:] = pop_by_age[:-1]
        pop_by_age[0] = new_babies
        if life_expectancy < max_age_limit:
            pop_by_age[life_expectancy:] = 0

    return history_years, history_total_pop, history_dep_ratio


# --- RUN & PLOT ---
years, total_pop, dep_ratio = run_simulation(start_dist_type, tfr, avg_birth_age, retire_age, life_expectancy)

# Plotting
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 10))

# Plot 1
ax1.plot(years, total_pop, color='#2c3e50', linewidth=2)
ax1.fill_between(years, total_pop, color='#2c3e50', alpha=0.1)
ax1.set_title("Total Population Size", fontsize=14, weight='bold')
ax1.grid(True, alpha=0.3)
ax1.set_ylim(bottom=0)

# Plot 2
ax2.plot(years, dep_ratio, color='#e74c3c', linewidth=2)
ax2.set_title("Dependency Ratio (%)", fontsize=14, weight='bold')
ax2.set_xlabel("Years from now")
ax2.grid(True, alpha=0.3)
ax2.axhline(y=50, color='green', linestyle='--', alpha=0.6, label='Dividend (<50%)')
ax2.legend()

plt.tight_layout()
st.pyplot(fig)