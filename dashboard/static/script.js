let toastTimer = null;
let selectedPatient = "P001";
let eventLogs = [];

const heartData = [];
const spo2Data = [];
const tempData = [];
const labels = [];


const heartChart = new Chart(
    document.getElementById("heartChart"),
    {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: "Heart Rate",
                data: heartData,
                borderColor: "red",
                fill: false,
                tension: 0.3
            }]
        }
    }
);

const spo2Chart = new Chart(
    document.getElementById("spo2Chart"),
    {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: "SpO₂",
                data: spo2Data,
                borderColor: "green",
                fill: false,
                tension: 0.3
            }]
        }
    }
);

const tempChart = new Chart(
    document.getElementById("tempChart"),
    {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: "Temperature",
                data: tempData,
                borderColor: "blue",
                fill: false,
                tension: 0.3
            }]
        }
    }
);

function showToast(message) {

    const toast = document.getElementById("toastNotification");
    const text = document.getElementById("toastMessage");

    text.innerHTML = message;

    toast.style.display = "block";

    if (toastTimer) {
        clearTimeout(toastTimer);
    }

    toastTimer = setTimeout(() => {

        toast.style.display = "none";

    }, 4000);

}
let alertedPatients = [];



async function loadPatients() {

    const response = await fetch("/patients");
    const result = await response.json();

    const patients = result.patients;

    document.getElementById("total").innerHTML =
        result.summary.total;

    document.getElementById("normal").innerHTML =
        result.summary.normal;

    document.getElementById("critical").innerHTML =
        result.summary.critical;

    document.getElementById("updated").innerHTML =
        result.summary.updated;

    let tableBody = document.getElementById("tableBody");
    tableBody.innerHTML = "";

    let criticalFound = false;

    patients.forEach(patient => {

        let rowClass = "";
        let statusText = "🟢 Normal";

        if (patient.status === "CRITICAL") {

            rowClass = "critical-row";
            statusText = "🔴 Critical";
            criticalFound = true;

            if (!alertedPatients.includes(patient.patient_id)) {

                showToast(
                     "🚨 Critical Patient : " +
                    patient.patient_id +
                    "<br>❤️ HR : " +
                    patient.heart_rate +
                    " | 🫁 SpO₂ : " +
                     patient.spo2
                 );
                 addLog("🚨 " + patient.patient_id + " became CRITICAL");

                 alertedPatients.push(patient.patient_id);

}
        } else {

            alertedPatients = alertedPatients.filter(
                id => id !== patient.patient_id
            );

        }

        tableBody.innerHTML += `
           <tr
           class="${rowClass} ${patient.patient_id === selectedPatient ? "selected-row" : ""}"
           onclick="loadHistory('${patient.patient_id}')"
           style="cursor:pointer;"> 
                <td>${patient.patient_id}</td>
                <td>${patient.heart_rate}</td>
                <td>${patient.spo2}</td>
                <td>${patient.bp_systolic}</td>
                <td>${patient.temperature}</td>
                <td>${statusText}</td>
            </tr>
        `;

    });
    
    
if (patients.length > 0) { 

    const selected = patients.find(
    p => p.patient_id === selectedPatient
);

if (selected) {
    document.getElementById("detailId").innerHTML =
    selected.patient_id;

    document.getElementById("detailStatus").innerHTML =
    selected.status;

   document.getElementById("detailHeart").innerHTML =
   selected.heart_rate + " bpm";

   document.getElementById("detailSpo2").innerHTML =
   selected.spo2 + " %";

  document.getElementById("detailBP").innerHTML =
  selected.bp_systolic + " mmHg";

  document.getElementById("detailTemp").innerHTML =
  selected.temperature + " °F";

  document.getElementById("detailTime").innerHTML =
  selected.timestamp;
  // AI Risk Score
let risk = 0;

risk += Math.max(0, selected.heart_rate - 80);

risk += Math.max(0, 95 - selected.spo2) * 8;

risk += Math.max(0, selected.temperature - 98) * 15;


risk = Math.min(100, Math.round(risk));
if (selected.status === "CRITICAL") {
    risk = 100;
}

document.getElementById("riskPercent").innerHTML =
    risk + "%";

const bar = document.getElementById("riskBar");

bar.style.width = risk + "%";

if (risk < 30) {

    document.getElementById("riskStatus").innerHTML =
        "🟢 LOW RISK";

    bar.style.background = "#2ecc71";

}
else if (risk < 70) {

    document.getElementById("riskStatus").innerHTML =
        "🟡 MEDIUM RISK";

    bar.style.background = "#f39c12";

}
else {

    document.getElementById("riskStatus").innerHTML =
        "🔴 HIGH RISK";

    bar.style.background = "#e74c3c";

}

    labels.push(new Date().toLocaleTimeString());

    heartData.push(selected.heart_rate);

    spo2Data.push(selected.spo2);

    tempData.push(selected.temperature);

    if (labels.length > 20) {

        labels.shift();
        heartData.shift();
        spo2Data.shift();
        tempData.shift();

    }

    heartChart.update();
    spo2Chart.update();
    tempChart.update();

}
    document.getElementById("alertBanner").style.display =
        criticalFound ? "block" : "none";

}
}

loadPatients();
setInterval(loadPatients, 2000);

async function loadHistory(patientId) {
   
   

    selectedPatient = patientId;
    console.log("Clicked:", patientId);

    document.getElementById("heartTitle").innerHTML =
        "❤️ Heart Rate (" + patientId + ")";

    document.getElementById("spo2Title").innerHTML =
        "🫁 SpO₂ (" + patientId + ")";

    document.getElementById("tempTitle").innerHTML =
        "🌡 Temperature (" + patientId + ")";

    const response = await fetch("/history/" + patientId);

    const history = await response.json();
    const last20 = history.slice(-20);
    if (last20.length === 0) {
    return;
}


   const latest = last20[last20.length - 1];
   let risk = 0;

risk += Math.max(0, latest.heart_rate - 80);
risk += Math.max(0, 95 - latest.spo2) * 8;
risk += Math.max(0, latest.temperature - 98) * 15;

risk = Math.min(100, Math.round(risk));

if (latest.status === "CRITICAL") {
    risk = 100;
}

document.getElementById("riskPercent").innerHTML = risk + "%";

const bar = document.getElementById("riskBar");

bar.style.width = risk + "%";

if (risk < 30) {
    document.getElementById("riskStatus").innerHTML = "🟢 LOW RISK";
    bar.style.background = "#2ecc71";
}
else if (risk < 70) {
    document.getElementById("riskStatus").innerHTML = "🟡 MEDIUM RISK";
    bar.style.background = "#f39c12";
}
else {
    document.getElementById("riskStatus").innerHTML = "🔴 HIGH RISK";
    bar.style.background = "#e74c3c";
}


document.getElementById("detailId").innerHTML =
    latest.patient_id;

document.getElementById("detailStatus").innerHTML =
    latest.status;

document.getElementById("detailHeart").innerHTML =
    latest.heart_rate + " bpm";

document.getElementById("detailSpo2").innerHTML =
    latest.spo2 + " %";

document.getElementById("detailBP").innerHTML =
    latest.bp_systolic + " mmHg";

document.getElementById("detailTemp").innerHTML =
    latest.temperature + " °F";

document.getElementById("detailTime").innerHTML =
    latest.timestamp;
  labels.length = 0;
   heartData.length = 0;
   spo2Data.length = 0;
   tempData.length = 0;

let avgHeart = 0;
let avgSpo2 = 0;
let avgTemp = 0;
let criticalEvents = 0;

last20.forEach(record => {

    avgHeart += record.heart_rate;
    avgSpo2 += record.spo2;
    avgTemp += record.temperature;

    if(record.status === "CRITICAL"){
        criticalEvents++;
    }
    labels.push(record.timestamp);

    heartData.push(record.heart_rate);

    spo2Data.push(record.spo2);

    tempData.push(record.temperature);

});




avgHeart = (avgHeart / last20.length).toFixed(1);
avgSpo2 = (avgSpo2 / last20.length).toFixed(1);
avgTemp = (avgTemp / last20.length).toFixed(1);

document.getElementById("avgHeart").innerHTML = avgHeart;
document.getElementById("avgSpo2").innerHTML = avgSpo2;
document.getElementById("avgTemp").innerHTML = avgTemp;
document.getElementById("criticalCount").innerHTML = criticalEvents;


    heartChart.update();
    spo2Chart.update();
    tempChart.update();

    

}
function searchPatient() {

    const value = document
        .getElementById("searchPatient")
        .value
        .toUpperCase();

    const rows = document.querySelectorAll("#tableBody tr");

    rows.forEach(row => {

        const id = row.cells[0].innerText.toUpperCase();

        if (id.includes(value)) {

            row.style.display = "";

        } else {

            row.style.display = "none";

        }

    });

}

function sendAlert() {

    alert("🚨 Emergency Alert Sent Successfully!");

}

function notifyDoctor() {

    addLog("👨‍⚕ Doctor notified");

    alert("👨‍⚕ Doctor has been notified.");

}

function downloadReport() {

    addLog("📄 Report downloaded for " + selectedPatient);

    window.location.href =
        "/download/" + selectedPatient;

}

function addLog(message) {

    const time = new Date().toLocaleTimeString();

    eventLogs.unshift(time + " - " + message);

    if(eventLogs.length > 10){

        eventLogs.pop();

    }

    document.getElementById("eventLog").innerHTML =
        eventLogs.map(log =>
            `<div class="log-item">${log}</div>`
        ).join("");

}