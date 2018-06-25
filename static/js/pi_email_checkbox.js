/* static/js/pi_email_checkbox.js */

class email_checkbox_handler {
	constructor(id, email){
		this.email = email;

	  /* Add the checkbox and label */
		this.textbox = document.getElementById(id);
		this.label = document.createElement('label');
		this.label.style.display = 'block';
		this.checkbox = document.createElement('input');
		this.checkbox.type = 'checkbox';
		this.label.appendChild(this.checkbox);
		var text = document.createTextNode(" I am the PI ");
		this.label.appendChild(text);
		var container = this.textbox.parentElement;
		container.insertBefore(this.label,this.textbox);

		/* Hide the text box when the check box is checked */
		/* Closure structure, return a function build for this object */
		this.checkbox.onclick = (function( obj ){
			return function() {
				console.log('run');
				/* Template function, cls become the object */
				if(obj.checkbox.checked){
					obj.textbox.value = obj.email;
					obj.textbox.style.display = 'none';
				} else {
					obj.textbox.style.display = 'block';
				}
			}
		})( this ); /* Call with obj=this */

		/* Check if the initial email is the given email, the checkbox should then be checked */
		if(this.textbox.value == this.email)
			this.checkbox.checked = true;
		this.checkbox.onclick();
	}
}
