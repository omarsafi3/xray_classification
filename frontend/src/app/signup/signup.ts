import { Component } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { environment } from '../../environment/environment.dev';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-signup',
  standalone: true,
  imports: [RouterModule, CommonModule, FormsModule],
  templateUrl: './signup.html',
  styleUrls: ['../login/login.scss']
})
export class Signup {
  username: string = '';
  password: string = '';
  confirm_password: string = '';

  private apiUrl = environment.apiUrl + '/auth/signup';

  constructor(private http: HttpClient, private router: Router) {}

  onSubmit(): void {
  if (this.password !== this.confirm_password) {
    alert('Passwords do not match.');
    return;
  }

  this.http.post<{ message: string } | string>(this.apiUrl, {
  username: this.username,
  password: this.password
}, { responseType: 'text' as 'json' })  // pretend string is JSON
.subscribe({
  next: (res: any) => {
    const message = typeof res === 'string' ? res : res.message;
    alert(message);
    this.router.navigate(['/login']);
  },
  error: (err) => {
    console.error('Signup error:', err);
    const message = err.error?.message || err.error?.text || 'Signup failed. Please try again.';
    alert(message);
  }
});


}


}
