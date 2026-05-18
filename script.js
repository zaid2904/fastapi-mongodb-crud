// Backend API URL
const API_URL = "http://127.0.0.1:8000/students";


// ------------------------------------
// GET ALL STUDENTS
// ------------------------------------
async function getStudents() {

    // Send GET request
    const response = await fetch(API_URL);

    // Convert response into JSON
    const students = await response.json();

    // Get student list div
    const studentList = document.getElementById("studentList");

    studentList.innerHTML = "";

    // Loop through all students
    students.forEach(student => {

        // Add HTML dynamically
        studentList.innerHTML += `
        
            <div class="student-card">

                <h3>${student.name}</h3>

                <p>Age: ${student.age}</p>

                <p>Course: ${student.course}</p>

                <div class="actions">

                    <button
                        class="edit-btn"
                        onclick="editStudent(
                            '${student._id}',
                            '${student.name}',
                            '${student.age}',
                            '${student.course}'
                        )"
                    >
                        Edit
                    </button>

                    <button
                        class="delete-btn"
                        onclick="deleteStudent('${student._id}')"
                    >
                        Delete
                    </button>

                </div>

            </div>
        `;
    });
}


// ------------------------------------
// CREATE OR UPDATE STUDENT
// ------------------------------------
async function saveStudent() {

    // Get form values
    const name = document.getElementById("name").value;

    const age = document.getElementById("age").value;

    const course = document.getElementById("course").value;

    const studentId = document.getElementById("studentId").value;


    // Create object
    // Remove extra spaces
const trimmedName = name.trim();

const trimmedCourse = course.trim();


// ----------------------------
// VALIDATION
// ----------------------------

// Check empty name
if(trimmedName === ""){

    alert("Name is required");

    return;
}


// Check empty age
if(age === ""){

    alert("Age is required");

    return;
}


// Check invalid age
if(Number(age) <= 0){

    alert("Age must be greater than 0");

    return;
}


// Check empty course
if(trimmedCourse === ""){

    alert("Course is required");

    return;
}


// Final object
const studentData = {

    name: trimmedName,

    age: Number(age),

    course: trimmedCourse
};


    // ----------------------------
    // UPDATE
    // ----------------------------
    if(studentId){

        await fetch(`${API_URL}/${studentId}`, {

            method: "PUT",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(studentData)
        });

    }

    // ----------------------------
    // CREATE
    // ----------------------------
    else{

        await fetch(API_URL, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(studentData)
        });
    }


    // Clear form after save
    clearForm();

    // Reload students
    getStudents();
}


// ------------------------------------
// EDIT STUDENT
// ------------------------------------
function editStudent(id, name, age, course){

    // Fill form with old data
    document.getElementById("studentId").value = id;

    document.getElementById("name").value = name;

    document.getElementById("age").value = age;

    document.getElementById("course").value = course;
}


// ------------------------------------
// DELETE STUDENT
// ------------------------------------
async function deleteStudent(id){

    // Send DELETE request
    await fetch(`${API_URL}/${id}`, {

        method: "DELETE"
    });

    // Reload students
    getStudents();
}


// ------------------------------------
// CLEAR FORM
// ------------------------------------
function clearForm(){

    document.getElementById("studentId").value = "";

    document.getElementById("name").value = "";

    document.getElementById("age").value = "";

    document.getElementById("course").value = "";
}


// ------------------------------------
// LOAD STUDENTS ON PAGE LOAD
// ------------------------------------
getStudents();