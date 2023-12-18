// Example starter JavaScript for disabling form submissions if there are invalid fields
(() => {
    'use strict'

    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    const forms = document.querySelectorAll('.needs-validation-signUp')

    // Loop over them and prevent submission
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault()
                event.stopPropagation()
            }


            const passwordSignUp = form.passwordSignUp
            const password2SignUp = form.password2SignUp

            if (passwordSignUp.value != password2SignUp.value) {
                password2SignUp.setCustomValidity("Паролі не співпадають");
            } else{
                passwordSignUp.setCustomValidity("");
                password2SignUp.setCustomValidity("");
            }


            form.classList.add("was-validated")

        }, false)
    })
})()