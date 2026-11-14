import { useState } from "react";

function Packages({ packages, setPackages }) {
    const [destination, setDestination] = useState("")
    const [status, setStatus] = useState("")
    const [arrivalDate, setArrivalDate] = useState("")

    let filteredPackages = [...packages];

    if (destination !== "") {
        filteredPackages = filteredPackages.filter((pkg) => pkg.package_destination === destination);
    }
    if (status !== "") {
        filteredPackages = filteredPackages.filter((pkg) => pkg.package_status === status);
    }
    if (arrivalDate !== "") {
        filteredPackages = filteredPackages.filter((pkg) => pkg.package_arrival_date === arrivalDate);
    }

    return (
        <div>
            <h2>Packages Filter</h2>
            <label>Destination:
                <input type="text" value={destination} onChange={(e) => setDestination(e.target.value)} />
            </label>
            <label>Status:
                <input type="text" value={status} onChange={(e) => setStatus(e.target.value)} />
            </label>
            <label>Arrival Date:
                <input type="date" value={arrivalDate} onChange={(e) => setArrivalDate(e.target.value)} />
            </label>

            <ul>
                {filteredPackages.map((pkg) => (
                    <li key={pkg.package_id}>
                        {pkg.package_name} - {pkg.package_destination} ({pkg.package_status})
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default Packages;