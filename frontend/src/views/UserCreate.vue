<template>
    <div class="container d-flex justify-content-center text-center">
        <div class="card" style="width: 60rem; margin-top: 10rem;">
            <div class="card-body">
                <figure class="text-center">
                    <blockquote class="blockquote">
                        <h2><span class="badge text-bg-warning">New User</span></h2>
                    </blockquote>
                </figure>
                <form class="row g-3 needs-validation" @submit.prevent="createUser">
                    <div class="col-md-6">
                        <label for="login_id" class="form-label">Login ID : </label>
                        <input type="text" v-model="login_id" class="form-control" id="login_id" name="login_id" title="Please provide a Login ID!" required>
                        <div class="invalid-feedback">
                            Please provide a Login ID!
                        </div>
                    </div>
                    <div class="col-md-6">
                        <label for="login_password" class="form-label">Password : </label>
                        <input type="password" v-model="login_password" class="form-control" id="login_password" name="login_password" title="Password must be at least 8 characters long!" pattern="^.{8,}$" required>
                        <div class="invalid-feedback">
                            Password must be at least 8 characters long!
                        </div>
                    </div>
                    <div class="col-md-6">
                        <label for="user_fname" class="form-label">First Name : </label>
                        <input type="text" v-model="user_fname" class="form-control" id="user_fname" name="user_fname" title="Please provide user first name!" required>
                        <div class="invalid-feedback">
                            Please provide user first name!
                        </div>
                    </div>
                    <div class="col-md-6">
                        <label for="user_lname" class="form-label">Last Name : </label>
                        <input type="text" v-model="user_lname" class="form-control" id="user_lname" name="user_lname" title="Please provide user last name!" required>
                        <div class="invalid-feedback">
                            Please provide user last name!
                        </div>
                    </div>
                    <div class="col-md-6">
                        <label for="user_qualification" class="form-label">Qualification : </label>
                        <input type="text" v-model="user_qualification" class="form-control" id="user_qualification" name="user_qualification" title="Please provide highest qualification!" required>
                        <div class="invalid-feedback">
                            Please provide highest qualification!
                        </div>
                    </div>
                    <div class="col-md-6">
                        <label for="user_dob" class="form-label">DOB : YYYY-MM-DD</label>
                        <input type="text" v-model="user_dob" class="form-control" id="user_dob" name="user_dob" title="1985-02-21" pattern="\d{4}-\d{2}-\d{2}" required>
                        <div class="invalid-feedback">
                            Please provide date of birth!
                        </div>
                    </div>
                    <div style="padding: 1rem;">
                        <button type="submit" class="btn btn-secondary">Save</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'UserCreate',
    data() {
        return {
            login_id: '',
            login_password: '',
            user_fname: '',
            user_lname: '',
            user_qualification: '',
            user_dob: ''
        };
    },
    methods: {
        createUser() {
            fetch('http://127.0.0.1:5000/api/user', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    login_id: this.login_id,
                    login_password: this.login_password,
                    role_name: 'user',
                    user_fname: this.user_fname,
                    user_lname: this.user_lname,
                    user_qualification: this.user_qualification,
                    user_dob: this.user_dob
                })
            })
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error('User creation failed');
                }
            })
            .then(data => {
                // Handle successful user creation here
                console.log('User created successfully:', data);
                // Redirect to the user page or perform any other action
                this.$router.push('/');
            })
            .catch(error => {
                // Handle user creation error here
                console.error('Error:', error);
                alert('User creation failed. Please check your input.');
            });
        }
    }
};
</script>