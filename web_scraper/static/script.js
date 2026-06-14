async function scrape() {
  const url = document.getElementById("url").value;

  const extract = [];

  document.querySelectorAll('input[type="checkbox"]:checked').forEach((cb) => {
    extract.push(cb.value);
  });

  const response = await fetch("/scrape", {
    method: "POST",

    headers: {
      "Content-Type": "application/json",
    },

    body: JSON.stringify({
      url,
      extract,
    }),
  });

  const data = await response.json();

  document.getElementById("result").textContent = JSON.stringify(data, null, 4);
}
