// #include <bits/stdc++.h>
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <stack>
#include<map>
#include<set>

#define ll long long
using namespace std;

bool isprime(ll n){
    if(n<=1) return false;
    for(ll i=2;i<=sqrt(n);i++){
        if(n%i==0) return false;
    }
    return true;
}

ll gcd(ll a,ll b)
{
    if(!b)return a;
    return gcd(b,a%b);
}
bool static compare(pair<ll,ll>&a,pair<ll,ll>&b)
{
    return a.first>b.first;
}

void solve()
{
  ll k,i;
  cin>>k;
  vector<ll>vec(k);
  for(i=0;i<k;++i)
  {
    cin>>vec[i];
  }
  int cnt=0;
  for(auto itr:vec)
  {
    if(itr>=3)
    {
        cout<<"YES\n";
        return;
    }
    if(itr>=2)cnt++;
  }
  if(cnt>=2)
  {
    cout<<"YES\n";
    return;
  }
  cout<<"NO\n";
}
int main() {

    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; 
    cin >> t;
    while (t--) 
    solve();
    return 0;
}