export const summaryMetrics = [
  { label: "Orders Analyzed", value: "96,469" },
  { label: "Customers Segmented", value: "93,462" },
  { label: "Late Delivery Accuracy", value: "79.4%" },
  { label: "Selected Clusters", value: "4" }
];

export const lateDeliveryMetrics = {
  datasetRows: 96469,
  trainingRows: 77255,
  testRows: 19214,
  threshold: 0.6,
  accuracy: 0.7936,
  precision: 0.1663,
  recall: 0.5194,
  f1Score: 0.252,
  confusion: {
    tp: 668,
    tn: 14580,
    fp: 3348,
    fn: 618
  }
};

export const topFeatures = [
  ["order_month_2018-06", -0.3917],
  ["order_month_2018-03", 0.3499],
  ["order_month_2018-02", 0.2498],
  ["order_month_2017-11", 0.2483],
  ["customer_state_RJ", 0.2013],
  ["customer_state_SP", -0.1889],
  ["customer_state_BA", 0.1528],
  ["customer_state_other", 0.1501],
  ["customer_state_MG", -0.1483],
  ["seller_state_MA", 0.1039],
  ["product_weight_g", 0.1031]
];

export const segmentationProfiles = [
  {
    name: "High Value Loyalists",
    customers: 15718,
    avgOrders: 1.0,
    avgSpent: 352.52,
    avgReview: 4.2,
    avgDelay: -14.45,
    lateRate: 0,
    installments: 7.59,
    color: "#0f766e",
    action: "Protect with premium support, higher-service delivery, and upsell campaigns."
  },
  {
    name: "Stable Everyday Buyers",
    customers: 2892,
    avgOrders: 2.11,
    avgSpent: 309.4,
    avgReview: 4.24,
    avgDelay: -12.8,
    lateRate: 0.05,
    installments: 3.31,
    color: "#1d4ed8",
    action: "Target with repeat-purchase nudges, bundles, and cross-sell journeys."
  },
  {
    name: "At-Risk Delay Hit Customers",
    customers: 6212,
    avgOrders: 1.0,
    avgSpent: 175.64,
    avgReview: 2.32,
    avgDelay: 10.68,
    lateRate: 1,
    installments: 3.03,
    color: "#b91c1c",
    action: "Use service recovery messaging, delayed-order alerts, and logistics intervention."
  },
  {
    name: "Low Value Occasional Buyers",
    customers: 68640,
    avgOrders: 1.0,
    avgSpent: 115.48,
    avgReview: 4.31,
    avgDelay: -13.25,
    lateRate: 0,
    installments: 1.82,
    color: "#7c3aed",
    action: "Use lightweight onboarding flows, entry offers, and low-cost remarketing."
  }
];

export const stateRiskHighlights = [
  { state: "RJ", risk: 0.79 },
  { state: "BA", risk: 0.73 },
  { state: "MA", risk: 0.82 },
  { state: "SP", risk: 0.31 },
  { state: "MG", risk: 0.35 },
  { state: "PR", risk: 0.28 }
];

export const states = ["SP", "RJ", "MG", "BA", "PR", "SC", "RS", "MA", "CE", "PA"];
export const paymentTypes = ["credit_card", "boleto", "voucher", "debit_card"];
export const months = [
  "2017-07",
  "2017-08",
  "2017-11",
  "2018-02",
  "2018-03",
  "2018-06",
  "2018-07"
];
