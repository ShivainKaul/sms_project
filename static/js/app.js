function addSubjectRow() {
  const container = document.getElementById("subject-rows");
  const row = document.createElement("div");
  row.className = "subject-row";

  const gradeOptions = Array.from(document.querySelector(".sgrade").options)
    .map(o => `<option value="${o.value}">${o.value}</option>`)
    .join("");

  row.innerHTML = `
    <input class="sname" type="text" name="subject_name[]" placeholder="Subject" required>
    <input class="scredit" type="number" name="credits[]" placeholder="Credits" min="0" step="0.5" required>
    <select class="sgrade" name="grade[]" required>${gradeOptions}</select>
    <button type="button" class="btn small outline" onclick="this.parentElement.remove()">Remove</button>
  `;
  container.appendChild(row);
}
