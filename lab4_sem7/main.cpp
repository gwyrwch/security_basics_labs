#include <iostream>
#include <vector>
#include <algorithm>
#include <string>
#include <map>
#include <cmath>
#include <set>
#include <numeric>
#pragma GCC optimize("Ofast")
#pragma GCC optimize("unroll-loops")

using namespace std;

int binpow (int a, int n, int mod) {
	if (n == 0)
		return 1;
	if (n % 2 == 1)
		return 1LL * binpow(a, n-1, mod) * a % mod;
	else {
		int b = 1LL * binpow(a, n / 2, mod) % mod;
		return 1LL * b * b % mod;
	}
}

bool is_prime(int x) {
    for (int i = 2; i * i <= x; i++) {
        if (x % i == 0) {
            return false;
        }
    }

    return true;
}

int gen_prime_number(int m) {
	int n;

	do {
		n = rand() % 100 + m;
	} while (n > m && !is_prime(n));

	return n;
}


int powmod (int a, int b, int p) {
	int res = 1;
	while (b)
		if (b & 1)
			res = int (res * 1ll * a % p),  --b;
		else
			a = int (a * 1ll * a % p),  b >>= 1;
	return res;
}
 
int generator (int p) {
	vector<int> fact;
	int phi = p-1,  n = phi;
	for (int i=2; i*i<=n; ++i)
		if (n % i == 0) {
			fact.push_back (i);
			while (n % i == 0)
				n /= i;
		}
	if (n > 1)
		fact.push_back (n);
 
	for (int res=2; res<=p; ++res) {
		bool ok = true;
		for (size_t i=0; i<fact.size() && ok; ++i)
			ok &= powmod (res, phi / fact[i], p) != 1;
		if (ok)  return res;
	}
	return -1;
}

int gcd (int a, int b) {
	while (b) {
		a %= b;
		swap (a, b);
	}
	return a;
}

int decrypt(pair<int, int> enc_m, int x, int p) {
	int a = enc_m.first;
	int b = enc_m.second;

	int ans = binpow(a, p - 1 - x, p);
	ans = (b * ans) % p;

	return ans;
}

pair<int, int> encrypt(int m, int p, int g, int y) {
	if (m > p) {
		throw;
	}

	int k;

	do {
		k = rand() % (p - 1);
	} while (k > 1 && k < p - 1 && gcd(k, p - 1));


	int a = binpow(g, k, p);
	int b = binpow(y, k, p);
	b = (b * m) % p;

	return {a, b};
}

int main() {
	srand(time(0));
	freopen("input.txt", "r", stdin);

	int m;
	cin >>  m;  
	cout << "m = " << m << endl;

	int p = gen_prime_number(m);
	int g = generator(p);

	int x = -1;
	for (int i = 2; i < p - 1; i++) {
		if (gcd(p - 1, i) == 1)  {
			x = i;
			break;
		}
	}

	int y = binpow(g, x, p);

	cout << "p = " << p << "; g = " << g << endl;
	cout << "x = " << x << "; y = " << y << endl;

	auto enc = encrypt(m, p, g, y);
	auto ans = decrypt(enc, x, p);
	cout << "enc: " << "{a = " << enc.first << "; b = " << enc.second << "}" << endl;
	cout << "dec: " << ans << endl;

	return 0;
}  
