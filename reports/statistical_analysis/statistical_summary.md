# Statistical Analysis Output

## Hypothesis Tests

| test_name | metric | group_a | group_b | group_a_mean | group_b_mean | difference_a_minus_b | test_statistic | p_value_approx | significant_alpha_0_05 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| late_vs_nonlate_review_score | review_score | Late | Non-Late | 2.3357 | 4.2946 | -1.9589 | -96.7477 | 0.0 | True |
| repeat_vs_onetime_order_value | total_order_value | Repeat | One-time | 145.953 | 160.7331 | -14.7802 | -6.2498 | 4.108524631618593e-10 | True |
| anova_review_score_by_state | review_score | customer_state | all_states | nan | nan | nan | 29.3355 | nan | True |

## Correlations Against Review Score

| feature | target | pearson_r | p_value_approx | sample_size |
| --- | --- | --- | --- | --- |
| total_order_value | review_score | -0.0407 | 0.0 | 96469 |
| delivery_time_days | review_score | -0.3265 | 0.0 | 96469 |
| delivery_delay_days | review_score | -0.2617 | 0.0 | 96469 |
| payment_installments | review_score | -0.0301 | 0.0 | 96469 |
| total_items | review_score | -0.1199 | 0.0 | 96469 |

## Regression Coefficients

| feature | coefficient |
| --- | --- |
| intercept | 4.7827 |
| delivery_delay_days | -0.0127 |
| delivery_time_days | -0.0353 |
| total_order_value | 0.0 |
| payment_installments | -0.0049 |
| total_items | -0.294 |

## Customer Value Segments

| value_segment | order_count | avg_order_value_brl | avg_review_score | avg_delivery_days | repeat_rate_pct |
| --- | --- | --- | --- | --- | --- |
| Low Value | 32162 | 49.07 | 4.24 | 10.8 | 6.39 |
| Mid Value | 32152 | 106.74 | 4.17 | 12.19 | 6.22 |
| High Value | 32155 | 323.68 | 4.08 | 13.29 | 5.8 |
