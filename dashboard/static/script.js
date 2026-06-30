async function loadPatients() {
    const response = await fetch("/patients");
    const patients = await response.json();

    const tableBody = document.getElementById("tableBody");
    tableBody.innerHTML = "";

    patients.forEach(patient => {

        let statusClass =
            patient.status === "CRITICAL"
            ? "critical"
            : "normal";

        let statusEmoji =
            patient.status === "CRITICAL"
            ? "🔴 Critical"
            : "🟢 Normal";

        tableBody.innerHTML += `
            <tr>
                <td>${patient.patient_id}</td>
                <td>${patient.heart_rate}</td>
                <td>${patient.spo2}</td>
                <td>${patient.bp_systolic}</td>
                <td>${patient.temperature}</td>
                <td class="${statusClass}">
                    ${statusEmoji}
                </td>
            </tr>
        `;
    });

}

loadPatients();

setInterval(loadPatients, 2000);