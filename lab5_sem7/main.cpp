#include <iostream>
#include <vector>
#include <algorithm>
#include <string>
#include <map>
#include <cmath>
#include <set>
#include <numeric>

using namespace std;

void prepare_string(string& s) {
	s += '1';

		while (s.size() % 512 != 448) {
		s += '0';
	}
}

string to_binary_str(unsigned n, int size) {
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

unsigned to_int(string s) {
	reverse(s.begin(), s.end());
	unsigned ans = 0;

	for (size_t i = 0; i < s.size(); i++) {
		ans += (s[i] - '0') * (1U << i);
	}

	return ans;
}


unsigned funF(unsigned x, unsigned y, unsigned z) {
	return (x & y) | ((~x) & z);
}

unsigned funG(unsigned x, unsigned y, unsigned z) {
	return (x & z) | ((~z) & y);
}

unsigned funH(unsigned x, unsigned y, unsigned z) {
	return x ^ y ^ z;
}

unsigned funI(unsigned x, unsigned y, unsigned z) {
	return y ^ ((~z) | x);
}

unsigned A = 0x67452301;
unsigned B = 0xEFCDAB89;
unsigned C = 0x98BADCFE;
unsigned D = 0x10325476;


vector<vector<int>> S = {
	{ 7, 12, 17, 22,  7, 12, 17, 22,  7, 12, 17, 22,  7, 12, 17, 22 },
	{ 5,  9, 14, 20,  5,  9, 14, 20,  5,  9, 14, 20,  5,  9, 14, 20 },
	{ 4, 11, 16, 23,  4, 11, 16, 23,  4, 11, 16, 23,  4, 11, 16, 23 },
	{ 6, 10, 15, 21,  6, 10, 15, 21,  6, 10, 15, 21,  6, 10, 15, 21 }
};


vector<string> break_into(const string& s, int block_size) {
	if (s.size() % block_size != 0)
		throw;

	vector<string> ans;
	for (int i = 0; i < s.size(); i += block_size) {
		string t;
		for (int j = i; j < i + block_size; j++) {
			t += s[j];
		}

		ans.push_back(t);
	}

	return ans;
}

unsigned shift(unsigned x, int c) {
	// return (x >> c) | (x << (32 -2 c));
	return (x << c)  | (x >> (32 - c));
}

unsigned t[64];

int main() {
	srand(time(0));
	freopen("input.txt", "r", stdin);

	string s; cin >> s;
	int l = s.size();


	prepare_string(s);
	s += to_binary_str(l, 64);

	for (int i = 0; i < 64; i++) {
		t[i] = (unsigned)((1ll << 32) * abs(sin(i + 1)));
	}

	vector<string> blocks_512 = break_into(s, 512);

	for (auto block : blocks_512) {
		unsigned a0 = A;
		unsigned b0 = B;
		unsigned c0 = C;
		unsigned d0 = D;
		
		vector<string> x = break_into(block, 32);

		for (auto& w : x) {
			reverse(w.begin(), w.end());

			for (int i = 0; i < w.size(); i += 8) {
				reverse(w.begin() + i, w.begin() + i + 8);
			}
		}

		for (int i = 0; i < 4; i++) {
			for (int j = 0; j < 16; j++) {
				unsigned index = i * 16 + j;
				unsigned x_index;
				unsigned func;
				
				// cout << b0 << ' ' << c0 << ' ' << d0 << endl;
				switch(i) {
					case 0:
						x_index = index;
						func = funF(b0, c0, d0);
						break;
					case 1:
						x_index = (index * 5 + 1) % 16;
						func = funG(b0, c0, d0);
						break;
					case 2:
						x_index = (index * 3 + 5) % 16;
						func = funH(b0, c0, d0);
						break;
					case 3:
						x_index = (index * 7) % 16;
						func = funI(b0, c0, d0);
						break;
				}
				
				func += a0 + t[index] + to_int(x[x_index]);
				

				a0 = d0;
				d0 = c0;
				c0 = b0;
				b0 = b0 + shift(func, S[i][j]);
			}	
		}

		A += a0;
		B += b0;
		C += c0;
		D += d0;
	}

	printf("%08x", htonl(A));
	printf("%08x", htonl(B));
	printf("%08x", htonl(C));
	printf("%08x", htonl(D));
	return 0;
}  
