# Default of Credit Card Clients

30,000 credit card clients of a Taiwanese bank, from April to September 2005: their
credit limit, demographics, six months of repayment status, bill statements and
payments, and whether they defaulted on their payment the next month (22.1% did).

## Files

- `credit-default.csv`: the original `default of credit card clients.xls`, converted to
  CSV with pandas (`read_excel(..., header=1)`), with its columns renamed as below and
  nothing else changed. Every value is an integer; there are no missing values.

## Columns

| Column | Original | Content |
| --- | --- | --- |
| `id` | `ID` | Client number, 1 to 30,000 |
| `limit` | `LIMIT_BAL` (X1) | Amount of the given credit, in NT dollars, the client's and their family's (supplementary) credit together |
| `sex` | `SEX` (X2) | 1 = male, 2 = female |
| `education` | `EDUCATION` (X3) | 1 = graduate school, 2 = university, 3 = high school, 4 = others; 0, 5 and 6 (345 clients) are undocumented |
| `marriage` | `MARRIAGE` (X4) | 1 = married, 2 = single, 3 = others; 0 (54 clients) is undocumented |
| `age` | `AGE` (X5) | Age, in years |
| `delay_sep` … `delay_apr` | `PAY_0`, `PAY_2` … `PAY_6` (X6–X11) | Repayment status in September, August, July, June, May and April 2005: -1 = paid duly, 1 to 8 = payment delay of that many months, 9 = nine months and more; -2 and 0 are not documented by the source, and 0 is the most frequent value |
| `bill_sep` … `bill_apr` | `BILL_AMT1` … `BILL_AMT6` (X12–X17) | Amount of the bill statement in September … April 2005, in NT dollars (negative: a credit balance) |
| `paid_sep` … `paid_apr` | `PAY_AMT1` … `PAY_AMT6` (X18–X23) | Amount paid in September … April 2005, in NT dollars |
| `default` | `default payment next month` (Y) | 1 = the client defaulted, 0 = they didn't |

The original names skip `PAY_1`; here every monthly column is named after its month.

## Source

- UCI Machine Learning Repository: https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients
  (`default of credit card clients.xls`, downloaded 2026-10)
- Yeh, I. (2009). Default of Credit Card Clients [Dataset]. UCI Machine Learning
  Repository. https://doi.org/10.24432/C55S3H
- Paper: I-Cheng Yeh and Che-hui Lien, "The comparisons of data mining techniques for the
  predictive accuracy of probability of default of credit card clients", *Expert Systems
  with Applications*, 36(2):2473-2480, 2009.

## License

CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).
