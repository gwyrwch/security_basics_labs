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

int gen_prime_number() {
	int n;
	do {
		n = rand() % 10000 + 1000;
	} while (!is_prime(n));

	return n;
}

int gcd (int a, int b) {
	while (b) {
		a %= b;
		swap (a, b);
	}
	return a;
}

int gen_d(int f_n) {
	for (int i = 2; i < f_n; i++) {
		if (gcd(f_n, i) == 1)
			return i;
	}

	return -1;
}

int gcdex (int a, int b, int & x, int & y) {
	// ax + my = 1
	// x - обратный элемент в кольце по модулю
	if (a == 0) {
	x = 0; y = 1;
	return b;
	}
	int x1, y1;
	int d = gcdex (b % a, a, x1, y1);
	x = y1 - (b / a) * x1;
	y = x1;
	return d;
}

int calc_e(int a, int m) {
	int x, y;
	int g = gcdex (a, m, x, y);
	if (g != 1)
		return -1;
	else {
		x = (x % m + m) % m;
		return x;
	}
}

string prepare_s(string s, int len) {
	reverse(s.begin(), s.end());
	s.push_back('1');

	while (s.size() % len != 0) {
		s.push_back('0');
	}

	reverse(s.begin(), s.end());
	return s;
}

vector<string> prepare_blocks(string s, int len) {
	int cnt = s.size() / len;
	vector<string> res;

	for (int i = 0; i < cnt; i++) {
		string t;
		for (int j = len * i; j < len * i + len; j++) {
			t.push_back(s[j]);
		}
		res.push_back(t);
	}

	return res;
}

int to_int(string s) {
	reverse(s.begin(), s.end());
	int ans = 0;

	for (int i = 0; i < s.size(); i++) {
		ans += (s[i] - '0') * (1 << i);
	}

	return ans;
}

string to_binary_str(int n, int size) {
    string ans;
    
    while (n > 0) {
        ans.push_back('0' + (n % 2));
        n /= 2;
    }

    while(ans.size() < size) {
    	ans.push_back('0');
    }
    
    reverse(ans.begin(), ans.end());
    
    return ans;
}

string decrypt(const vector<int> &enc_nums, int d, int n, int bin_size) {
	string ans;
	for (int i = 0; i < enc_nums.size(); i++) {
		int dec = binpow(enc_nums[i], d, n);

		string dec_str = to_binary_str(dec, bin_size); 
		ans += dec_str;
	}

	reverse(ans.begin(), ans.end());
	while (ans.back() != '1') {
		ans.pop_back();
	}
	ans.pop_back();
	reverse(ans.begin(), ans.end());
	return ans;
}

vector<int> encrypt(vector<string> blocks, int e, int n) {
	vector<int> enc_nums;
	for (const auto &block : blocks) {
		int m = to_int(block);
		int enc = binpow(m, e, n);
		enc_nums.push_back(enc);
	}

	return enc_nums;
}

int main() {
	srand(time(0));
	freopen("input.txt", "r", stdin);

	int p = gen_prime_number();
	int q = gen_prime_number();

	cout << "p = " << p << ", q = " << q << endl;

	int n = p * q;
	cout << "n = " << n << endl;

	int f_n = (p - 1) * (q - 1);
	cout << "F(n) = " << f_n << endl;
	int d = gen_d(f_n);
	cout << "d = " << d << endl;

	pair<int, int> open_key, private_key;

	int e = calc_e(d, f_n);

	cout << "e = " << e << endl;

	if (((d * e) % f_n) != 1) {
		throw;
	}

	open_key = {e, n};
	private_key = {d, n};

	int len = 0;
	while ((1 << (len + 1)) < n) {
		len++;
	}

	string s;
	cin >> s;
	
	cout << "init = " <<  s << endl;
	s = prepare_s(s, len);
	
	vector<string> blocks = prepare_blocks(s, len);

	vector<int> enc_nums = encrypt(blocks, e, n);

	string dec = decrypt(enc_nums, d, n, len);
	cout << " ans = " << dec << endl;

	return 0;
}  
