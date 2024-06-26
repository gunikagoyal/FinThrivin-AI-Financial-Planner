import pulp

def optimize_allocation_pulp(user_data):
    total_funds = user_data['total_budget']
    prob = pulp.LpProblem("BudgetDistribution", pulp.LpMaximize)

    # Define decision variables
    expense = pulp.LpVariable('Expense', lowBound=user_data['bounds']['expense_min'], upBound=user_data['bounds']['expense_max'])
    emergency_fund = pulp.LpVariable('EmergencyFund', lowBound=user_data['bounds']['emergency_fund_min'] * total_funds / 100, upBound=user_data['bounds']['emergency_fund_max'] * total_funds / 100)
    short_term_goals = pulp.LpVariable('ShortTermGoals', lowBound=0, upBound=sum(goal['amount'] for goal in user_data['short_term_goals']))
    debt_payment = pulp.LpVariable('DebtPayment', lowBound=user_data['bounds']['debt_payment_min'] * total_funds / 100, upBound=user_data['bounds']['debt_payment_max'] * total_funds / 100)
    long_term_goals = pulp.LpVariable('LongTermGoals', lowBound=user_data['bounds']['long_term_goals_min'] * total_funds / 100, upBound=user_data['bounds']['long_term_goals_max'] * total_funds / 100)

    # Objective function
    prob += (
        user_data['weights']['Expense'] * expense +
        user_data['weights']['Emergency Fund'] * emergency_fund +
        user_data['weights']['Short-Term Goals'] * short_term_goals +
        user_data['weights']['Debt Payment'] * debt_payment +
        user_data['weights']['Long-Term Goals'] * long_term_goals
    )

    # Constraints
    prob += expense + emergency_fund + short_term_goals + debt_payment + long_term_goals <= total_funds

    # Solve the problem
    prob.solve(pulp.PULP_CBC_CMD(msg=True))

    if pulp.LpStatus[prob.status] == 'Optimal':
        return {
            'expense': expense.varValue,
            'emergency_fund': emergency_fund.varValue,
            'short_term_goal': short_term_goals.varValue,
            'debt_payment': debt_payment.varValue,
            'long_term_goals': long_term_goals.varValue
        }
    else:
        raise ValueError("Optimization failed to find a solution.")
