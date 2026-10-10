#include <iostream>
#include <vector>
using namespace std;

bool halloumiBoxes(vector<int> a, int k){
    int n = a.size();
    int count = 0, count_max = 0;
    if (n<=k){
        return true;
    }
    else if(k==1){
        for(int i =0; i<n-1; i++){
            if(a[i]>a[i+1]){
                return false;
            }
            else {
                continue;
            }
        }
        return true;
    }
    else {
        for(int i = 0; i< n-1; i++){
            if(a[i]>a[i+1]){
                count += 1;
            }
            else{
                if (count_max < count){
                count_max = count;
                }
                count = 0;
            }
        }
        if(count_max > k){
            return false;
        }
        else{
            return true;
        }
    }
}

int main(){
    int t;
    cin >> t;
    vector<bool> b(t);
    for(int i=0; i<t; i++){
        int n, k;
        cin >> n >> k;
        if(n < 1 || k < 1){
            cout << "number of halloumi and reverse cannot be zero or lower";
            return 0;
        }
        vector<int> a(n);
        for(int j =0; j<n;j++){
            cin >> a[j];
        }
        b[i] = halloumiBoxes(a, k);
    }
    for(int i=0; i<t ; i++){
        if(b[i] == 1){
        cout << "Yes\n";}
        else{
            cout << "No\n";
        }
    }
    return 0;
}
