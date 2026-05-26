import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment';
import { AuthUser, LoginRequest, TokenResponse } from '../../models/auth.models';

const TOKEN_KEY = 'gst_access_token';
const REFRESH_KEY = 'gst_refresh_token';
const USER_KEY = 'gst_user';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly apiUrl = environment.apiUrl;
  private _isLoggedIn$ = new BehaviorSubject<boolean>(this.hasToken());

  isLoggedIn$ = this._isLoggedIn$.asObservable();

  constructor(private http: HttpClient, private router: Router) {}

  login(credentials: LoginRequest): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${this.apiUrl}/auth/login`, credentials).pipe(
      tap((res) => this.storeSession(res))
    );
  }

  logout(): void {
    this.http.post(`${this.apiUrl}/auth/logout`, {}).subscribe({ error: () => {} });
    this.clearSession();
    this.router.navigate(['/login']);
  }

  refreshToken(): Observable<TokenResponse> {
    const refresh = localStorage.getItem(REFRESH_KEY) ?? '';
    return this.http.post<TokenResponse>(`${this.apiUrl}/auth/refresh`, { refresh_token: refresh }).pipe(
      tap((res) => this.storeSession(res))
    );
  }

  getAccessToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  }

  getUser(): AuthUser | null {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? (JSON.parse(raw) as AuthUser) : null;
  }

  private hasToken(): boolean {
    return !!localStorage.getItem(TOKEN_KEY);
  }

  private storeSession(res: TokenResponse): void {
    localStorage.setItem(TOKEN_KEY, res.access_token);
    localStorage.setItem(REFRESH_KEY, res.refresh_token);
    localStorage.setItem(USER_KEY, JSON.stringify({ username: res.username, role: res.role }));
    this._isLoggedIn$.next(true);
  }

  private clearSession(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem(USER_KEY);
    this._isLoggedIn$.next(false);
  }
}
