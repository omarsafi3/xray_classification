import { Component } from '@angular/core';
import { Router, RouterModule } from '@angular/router'; 
import { AuthService } from '../services/auth.service';
import { FormsModule } from '@angular/forms'; 

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [RouterModule, FormsModule], 
  templateUrl: './login.html',
  styleUrls: ['./login.scss'] 
})
export class Login {
  username: string = '';
  password: string = '';

  constructor(private authService: AuthService, private router: Router) {}

  onSubmit(): void {
    this.authService.login(this.username, this.password).subscribe({
      next: () => {
        this.router.navigate(['/home']);
      },
      error: (err: any) => {
        console.error('Login failed:', err);
        alert('Invalid credentials');
      }
    });
  }
}
