import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { User } from '../models/user';
import { environment} from '../../environment/environment.dev';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
    getToken(): any | null {
    return localStorage.getItem('access_token');
}

  private apiUrl = environment.apiUrl+'/auth';

  constructor(private http: HttpClient) { }

login(username: string, password: string): Observable<any> {
  return this.http.post<{ token: string }>(`${this.apiUrl}/signin`, { username, password })
    .pipe(
      tap(response => {
        const rawToken = response.token;
        localStorage.setItem('access_token', rawToken); 
        console.log('Saved token:', rawToken);
      })
    );
}



  logout() {
    localStorage.removeItem('access_token');
  }

  public get loggedIn(): boolean {
    return localStorage.getItem('access_token') !== null;
  }

  get currentUser(): User | null 
 {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return null;
    }
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.user;
  } }