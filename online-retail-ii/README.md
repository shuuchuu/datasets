# Online Retail II

Every invoice line of a UK-based online retailer of all-occasion gift-ware (many of its
customers are wholesalers), from 1 December 2009 to 9 December 2011.

## Files

- `online_retail_II.csv.gz`: 1,044,848 invoice lines, gzipped CSV with a header row:
  `Invoice` (a number; one starting with `C` is a cancellation), `StockCode` (the
  product; `POST`, `M`, `DOT`, `BANK CHARGES`… are not products), `Description`,
  `Quantity`, `InvoiceDate` (`YYYY-MM-DD HH:MM:SS`), `Price` (unit price, pounds
  sterling), `Customer ID` (empty for 235,287 lines), `Country`.

## Source

- UCI Machine Learning Repository: https://archive.ics.uci.edu/dataset/502/online+retail+ii
  (`online+retail+ii.zip`, downloaded 2026-11-19)
- Chen, D. (2012). Online Retail II [Dataset]. UCI Machine Learning Repository.
  https://doi.org/10.24432/C5CG6D

The original is an Excel workbook with one sheet per year ("Year 2009-2010", "Year
2010-2011"). The sheets overlap: the 22,523 lines from 1 to 9 December 2010 are in both,
identical. The CSV concatenates the two sheets, without the first one's copy of those
lines (1,067,371 − 22,523 = 1,044,848 lines), in the workbook's order; `Customer ID`
is written as an integer. Nothing else is changed: the cancellations, the lines without
a customer and the duplicate lines within an invoice are kept.

## License

CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).
