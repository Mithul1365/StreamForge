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

                alert("🚨 Critical Patient : " + patient.patient_id);

                alertedPatients.push(patient.patient_id);

            }

        } else {

            alertedPatients = alertedPatients.filter(
                id => id !== patient.patient_id
            );

        }

        tableBody.innerHTML += `
            <tr class="${rowClass}">
                <td>${patient.patient_id}</td>
                <td>${patient.heart_rate}</td>
                <td>${patient.spo2}</td>
                <td>${patient.bp_systolic}</td>
                <td>${patient.temperature}</td>
                <td>${statusText}</td>
            </tr>
        `;

    });

    document.getElementById("alertBanner").style.display =
        criticalFound ? "block" : "none";

}

loadPatients();

setInterval(loadPatients, 2000);