import { segmentationProfiles } from "../data/mlData";

const stateBoost = {
  MA: 0.18,
  RJ: 0.14,
  BA: 0.11,
  CE: 0.1,
  PA: 0.08,
  SP: -0.08,
  MG: -0.05,
  PR: -0.05
};

const monthBoost = {
  "2018-03": 0.16,
  "2018-02": 0.11,
  "2017-11": 0.11,
  "2018-06": -0.18,
  "2018-07": -0.07,
  "2017-07": -0.05,
  "2017-08": -0.04
};

export function predictLateDeliveryRisk(form) {
  let score = -1.1;

  score += stateBoost[form.customerState] ?? 0.03;
  score += (stateBoost[form.sellerState] ?? 0) * 0.35;
  score += monthBoost[form.orderMonth] ?? 0;
  score += form.productWeightG > 2000 ? 0.12 : 0;
  score += form.totalFreight > 40 ? 0.08 : 0;
  score += form.totalItems > 2 ? 0.06 : 0;
  score += form.paymentType === "boleto" ? 0.04 : 0;
  score += form.totalOrderValue > 250 ? 0.03 : 0;
  score += form.paymentInstallments >= 8 ? 0.02 : 0;

  const probability = 1 / (1 + Math.exp(-score));

  const drivers = [
    { label: `Customer state: ${form.customerState}`, impact: stateBoost[form.customerState] ?? 0.03 },
    { label: `Seller state: ${form.sellerState}`, impact: (stateBoost[form.sellerState] ?? 0) * 0.35 },
    { label: `Order month: ${form.orderMonth}`, impact: monthBoost[form.orderMonth] ?? 0 },
    { label: "Product weight", impact: form.productWeightG > 2000 ? 0.12 : 0 },
    { label: "Freight value", impact: form.totalFreight > 40 ? 0.08 : 0 }
  ]
    .sort((a, b) => Math.abs(b.impact) - Math.abs(a.impact))
    .slice(0, 3);

  let label = "Low Risk";
  if (probability >= 0.6) label = "High Risk";
  else if (probability >= 0.4) label = "Medium Risk";

  return {
    probability,
    label,
    drivers
  };
}

export function assignCustomerSegment(form) {
  if (form.lateDeliveryRate >= 0.8 || form.avgDelay >= 5 || form.avgReviewScore <= 2.8) {
    return segmentationProfiles.find((segment) => segment.name === "At-Risk Delay Hit Customers");
  }

  if (form.totalSpent >= 300 && form.paymentInstallments >= 5) {
    return segmentationProfiles.find((segment) => segment.name === "High Value Loyalists");
  }

  if (form.totalOrders >= 2) {
    return segmentationProfiles.find((segment) => segment.name === "Stable Everyday Buyers");
  }

  return segmentationProfiles.find((segment) => segment.name === "Low Value Occasional Buyers");
}
