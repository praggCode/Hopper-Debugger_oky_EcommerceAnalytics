import { useState } from "react";
import MetricCard from "./components/MetricCard";
import SectionCard from "./components/SectionCard";
import BarViz from "./components/BarViz";
import {
  lateDeliveryMetrics,
  months,
  paymentTypes,
  segmentationProfiles,
  stateRiskHighlights,
  states,
  summaryMetrics,
  topFeatures
} from "./data/mlData";
import { fetchCustomerSegment, fetchLateDeliveryPrediction } from "./services/api";

const tabs = [
  { id: "overview", label: "Overview" },
  { id: "predictor", label: "Delivery Check" },
  { id: "segments", label: "Customer Groups" },
  { id: "insights", label: "Model Summary" }
];

const initialRiskForm = {
  customerState: "RJ",
  sellerState: "SP",
  paymentType: "credit_card",
  paymentInstallments: 4,
  totalItems: 1,
  totalOrderValue: 180,
  totalFreight: 32,
  productWeightG: 1200,
  orderMonth: "2018-03"
};

const initialSegmentForm = {
  totalOrders: 1,
  totalSpent: 220,
  avgReviewScore: 4.0,
  avgDelay: -6,
  lateDeliveryRate: 0,
  paymentInstallments: 4
};

const riskPresets = [
  {
    name: "Low risk example",
    values: {
      customerState: "SP",
      sellerState: "SP",
      paymentType: "boleto",
      paymentInstallments: 1,
      totalItems: 1,
      totalOrderValue: 120,
      totalFreight: 18,
      productWeightG: 600,
      orderMonth: "2018-06"
    }
  },
  {
    name: "High risk example",
    values: {
      customerState: "RJ",
      sellerState: "MA",
      paymentType: "credit_card",
      paymentInstallments: 7,
      totalItems: 2,
      totalOrderValue: 360,
      totalFreight: 54,
      productWeightG: 2800,
      orderMonth: "2018-03"
    }
  }
];

const segmentPresets = [
  {
    name: "High value customer",
    values: {
      totalOrders: 3,
      totalSpent: 890,
      avgReviewScore: 4.7,
      avgDelay: -12,
      lateDeliveryRate: 0,
      paymentInstallments: 8
    }
  },
  {
    name: "At-risk customer",
    values: {
      totalOrders: 1,
      totalSpent: 175,
      avgReviewScore: 2.1,
      avgDelay: 9,
      lateDeliveryRate: 1,
      paymentInstallments: 3
    }
  }
];

export default function App() {
  const [activeTab, setActiveTab] = useState("overview");
  const [riskForm, setRiskForm] = useState(initialRiskForm);
  const [segmentForm, setSegmentForm] = useState(initialSegmentForm);
  const [prediction, setPrediction] = useState(null);
  const [assignedSegment, setAssignedSegment] = useState(null);
  const [riskLoading, setRiskLoading] = useState(false);
  const [segmentLoading, setSegmentLoading] = useState(false);
  const [riskError, setRiskError] = useState("");
  const [segmentError, setSegmentError] = useState("");

  async function handleRiskCheck() {
    setRiskLoading(true);
    setRiskError("");
    try {
      const result = await fetchLateDeliveryPrediction(riskForm);
      setPrediction(result);
    } catch {
      setRiskError("Backend not running. Start the backend to get a real prediction.");
    } finally {
      setRiskLoading(false);
    }
  }

  async function handleSegmentCheck() {
    setSegmentLoading(true);
    setSegmentError("");
    try {
      const result = await fetchCustomerSegment(segmentForm);
      setAssignedSegment(result);
    } catch {
      setSegmentError("Backend not running. Start the backend to get a real customer group.");
    } finally {
      setSegmentLoading(false);
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-block">
          <div className="brand-kicker">Olist E-Commerce ML</div>
          <h1>ML Dashboard</h1>
          <p>A simple view of delivery risk and customer groups.</p>
        </div>

        <nav className="tab-nav">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={tab.id === activeTab ? "active" : ""}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </nav>

        <div className="sidebar-note">
          This app now uses a small backend. Run the backend first to get live results.
        </div>
      </aside>

      <main className="main-panel">
        <header className="hero">
          <div className="hero-copy">
            <div className="hero-kicker">Simple Dashboard</div>
            <h2>Check delivery risk and understand customer types.</h2>
            <p>
              This frontend is designed for easy understanding. It keeps the ML results simple and
              avoids too much information at once.
            </p>
          </div>
        </header>

        <section className="metric-grid">
          <MetricCard
            label="Orders Used"
            value={summaryMetrics[0].value}
            hint="Orders included in the ML analysis"
          />
          <MetricCard
            label="Customers Grouped"
            value={summaryMetrics[1].value}
            hint="Customers included in segmentation"
          />
          <MetricCard
            label="Prediction Accuracy"
            value={summaryMetrics[2].value}
            hint="How often the delivery model was correct"
          />
          <MetricCard
            label="Customer Groups"
            value={summaryMetrics[3].value}
            hint="Total segments created by clustering"
          />
        </section>

        {activeTab === "overview" ? <OverviewTab /> : null}
        {activeTab === "predictor" ? (
          <PredictorTab
            form={riskForm}
            setForm={setRiskForm}
            prediction={prediction}
            onSubmit={handleRiskCheck}
            loading={riskLoading}
            error={riskError}
          />
        ) : null}
        {activeTab === "segments" ? (
          <SegmentationTab
            form={segmentForm}
            setForm={setSegmentForm}
            assignedSegment={assignedSegment}
            onSubmit={handleSegmentCheck}
            loading={segmentLoading}
            error={segmentError}
          />
        ) : null}
        {activeTab === "insights" ? <InsightsTab /> : null}
      </main>
    </div>
  );
}

function OverviewTab() {
  return (
    <div className="content-grid">
      <SectionCard eyebrow="About" title="What this dashboard does">
        <ul className="plain-list">
          <li>Delivery Check estimates whether an order looks risky for late delivery.</li>
          <li>Customer Groups shows what type of customer profile is being entered.</li>
          <li>Model Summary explains the results in a simple way.</li>
        </ul>
      </SectionCard>

      <SectionCard eyebrow="States" title="States with higher delivery risk">
        <BarViz
          items={stateRiskHighlights.map((item) => ({ label: item.state, value: item.risk }))}
          maxValue={1}
          formatter={(value) => `${Math.round(value * 100)}%`}
        />
      </SectionCard>

      <SectionCard eyebrow="Groups" title="Customer groups" className="span-two">
        <div className="segment-grid">
          {segmentationProfiles.map((segment) => (
            <div className="segment-card" key={segment.name}>
              <div className="segment-topline" style={{ color: segment.color }}>
                {segment.name}
              </div>
              <p>{segment.action}</p>
            </div>
          ))}
        </div>
      </SectionCard>
    </div>
  );
}

function PredictorTab({ form, setForm, prediction, onSubmit, loading, error }) {
  return (
    <div className="content-grid">
      <SectionCard eyebrow="Examples" title="Quick examples">
        <div className="preset-grid">
          {riskPresets.map((preset) => (
            <button
              key={preset.name}
              type="button"
              className="preset-card"
              onClick={() => setForm(preset.values)}
            >
              {preset.name}
            </button>
          ))}
        </div>
      </SectionCard>

      <SectionCard eyebrow="Input" title="Order details">
        <div className="form-grid">
          <SelectField
            label="Customer state"
            value={form.customerState}
            options={states}
            onChange={(value) => setForm({ ...form, customerState: value })}
          />
          <SelectField
            label="Seller state"
            value={form.sellerState}
            options={states}
            onChange={(value) => setForm({ ...form, sellerState: value })}
          />
          <SelectField
            label="Payment type"
            value={form.paymentType}
            options={paymentTypes}
            onChange={(value) => setForm({ ...form, paymentType: value })}
          />
          <SelectField
            label="Order month"
            value={form.orderMonth}
            options={months}
            onChange={(value) => setForm({ ...form, orderMonth: value })}
          />
          <NumberField
            label="Installments"
            value={form.paymentInstallments}
            onChange={(value) => setForm({ ...form, paymentInstallments: value })}
          />
          <NumberField
            label="Items"
            value={form.totalItems}
            onChange={(value) => setForm({ ...form, totalItems: value })}
          />
          <NumberField
            label="Order value"
            value={form.totalOrderValue}
            onChange={(value) => setForm({ ...form, totalOrderValue: value })}
          />
          <NumberField
            label="Freight"
            value={form.totalFreight}
            onChange={(value) => setForm({ ...form, totalFreight: value })}
          />
          <NumberField
            label="Weight (g)"
            value={form.productWeightG}
            onChange={(value) => setForm({ ...form, productWeightG: value })}
          />
        </div>
        <div className="action-line">
          <button type="button" className="primary-button" onClick={onSubmit} disabled={loading}>
            {loading ? "Checking..." : "Check delivery risk"}
          </button>
        </div>
      </SectionCard>

      <SectionCard eyebrow="Result" title="Delivery risk" className="result-card">
        {prediction ? (
          <div className="risk-panel">
            <div className={`risk-badge ${prediction.label.toLowerCase().replace(" ", "-")}`}>
              {prediction.label}
            </div>
            <div className="risk-probability">{Math.round(prediction.probability * 100)}%</div>
            <p>This result is coming from the backend model.</p>
          </div>
        ) : (
          <EmptyState text="Click the button to get a delivery risk result." />
        )}
        {error ? <div className="status-message error">{error}</div> : null}
      </SectionCard>

      <SectionCard eyebrow="Why" title="Top reasons" className="span-two">
        {prediction ? (
          <BarViz
            items={prediction.drivers.map((item) => ({ label: item.label, value: item.impact }))}
            formatter={(value) => (value >= 0 ? `+${value.toFixed(2)}` : value.toFixed(2))}
            maxValue={0.2}
          />
        ) : (
          <EmptyState text="The main reasons will appear here after you run a prediction." />
        )}
      </SectionCard>
    </div>
  );
}

function SegmentationTab({ form, setForm, assignedSegment, onSubmit, loading, error }) {
  return (
    <div className="content-grid">
      <SectionCard eyebrow="Examples" title="Quick examples">
        <div className="preset-grid">
          {segmentPresets.map((preset) => (
            <button
              key={preset.name}
              type="button"
              className="preset-card"
              onClick={() => setForm(preset.values)}
            >
              {preset.name}
            </button>
          ))}
        </div>
      </SectionCard>

      <SectionCard eyebrow="Input" title="Customer details">
        <div className="form-grid">
          <NumberField
            label="Total orders"
            value={form.totalOrders}
            onChange={(value) => setForm({ ...form, totalOrders: value })}
          />
          <NumberField
            label="Total spent"
            value={form.totalSpent}
            onChange={(value) => setForm({ ...form, totalSpent: value })}
          />
          <NumberField
            label="Review score"
            value={form.avgReviewScore}
            step="0.1"
            onChange={(value) => setForm({ ...form, avgReviewScore: value })}
          />
          <NumberField
            label="Delay (days)"
            value={form.avgDelay}
            onChange={(value) => setForm({ ...form, avgDelay: value })}
          />
          <NumberField
            label="Late rate"
            value={form.lateDeliveryRate}
            step="0.05"
            onChange={(value) => setForm({ ...form, lateDeliveryRate: value })}
          />
          <NumberField
            label="Installments"
            value={form.paymentInstallments}
            onChange={(value) => setForm({ ...form, paymentInstallments: value })}
          />
        </div>
        <div className="action-line">
          <button type="button" className="primary-button" onClick={onSubmit} disabled={loading}>
            {loading ? "Checking..." : "Find customer group"}
          </button>
        </div>
      </SectionCard>

      <SectionCard
        eyebrow="Result"
        title={assignedSegment ? assignedSegment.name : "Customer group"}
        className="result-card"
      >
        {assignedSegment ? (
          <div className="segment-result">
            <div className="segment-chip" style={{ backgroundColor: assignedSegment.color }}>
              Customer Group
            </div>
            <p>{assignedSegment.action}</p>
            <div className="mini-metrics">
              <span>Avg spend: BRL {assignedSegment.avgSpent}</span>
              <span>Avg review: {assignedSegment.avgReview}</span>
            </div>
          </div>
        ) : (
          <EmptyState text="Click the button to get a customer group." />
        )}
        {error ? <div className="status-message error">{error}</div> : null}
      </SectionCard>

      <SectionCard eyebrow="Reference" title="All groups" className="span-two">
        <div className="table-shell">
          <table>
            <thead>
              <tr>
                <th>Group</th>
                <th>Customers</th>
                <th>Avg Spent</th>
                <th>Avg Review</th>
              </tr>
            </thead>
            <tbody>
              {segmentationProfiles.map((segment) => (
                <tr key={segment.name}>
                  <td>{segment.name}</td>
                  <td>{segment.customers.toLocaleString()}</td>
                  <td>{segment.avgSpent}</td>
                  <td>{segment.avgReview}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </SectionCard>
    </div>
  );
}

function InsightsTab() {
  return (
    <div className="content-grid">
      <SectionCard eyebrow="Performance" title="Delivery model results">
        <div className="metric-inline-grid">
          <MetricCard label="Accuracy" value={`${(lateDeliveryMetrics.accuracy * 100).toFixed(1)}%`} />
          <MetricCard label="Precision" value={`${(lateDeliveryMetrics.precision * 100).toFixed(1)}%`} />
          <MetricCard label="Recall" value={`${(lateDeliveryMetrics.recall * 100).toFixed(1)}%`} />
          <MetricCard label="F1 Score" value={`${(lateDeliveryMetrics.f1Score * 100).toFixed(1)}%`} />
        </div>
      </SectionCard>

      <SectionCard eyebrow="Factors" title="Important features">
        <BarViz
          items={topFeatures.map(([label, value]) => ({ label, value }))}
          formatter={(value) => (value >= 0 ? `+${value.toFixed(2)}` : value.toFixed(2))}
          maxValue={0.4}
        />
      </SectionCard>

      <SectionCard eyebrow="Summary" title="Simple explanation" className="span-two">
        <ul className="plain-list">
          <li>The delivery model predicts whether an order may be late.</li>
          <li>The segmentation model groups customers with similar behavior.</li>
          <li>These two models help with delivery planning and customer targeting.</li>
        </ul>
      </SectionCard>
    </div>
  );
}

function EmptyState({ text }) {
  return <div className="empty-state">{text}</div>;
}

function SelectField({ label, value, options, onChange }) {
  return (
    <label className="field">
      <span>{label}</span>
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}

function NumberField({ label, value, onChange, step = "1" }) {
  return (
    <label className="field">
      <span>{label}</span>
      <input
        type="number"
        value={value}
        step={step}
        onChange={(event) => onChange(Number(event.target.value))}
      />
    </label>
  );
}
