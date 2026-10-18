#include <iostream>
#include <vector>
using namespace std;

int lineTrip(vector<int> a, int k){
    int n = a.size();
    int val =0, low=0;
    for(int i=0;i<n;i++){

    }
}

int main(){
    int t;
    cin >> t;
    vector<int> b(t);
    for(int i=0; i<t;i++){
        int n, k;
        cin >> n >> k;
        if(n>k || n<1 || k<1 ){
            cout << "Invalid values of either n or k";
        }
        vector<int> a(n);
        for(int j=0; j<n;j++){
            cin >> a[j];
            if (j>0){
                if(a[j]<a[j-1]){
                    cout << "Gas Station must be in a sorted manner";
                    return 0;
                }
            }
        }
        b[i] = lineTrip(a, k);
    }
}