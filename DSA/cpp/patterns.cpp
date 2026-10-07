#include <iostream>

using namespace std;

void rightAngledLeft(int n){
    int i,j;
    for (i=0;i<n;i++){
        for (j=0; j<i; j++){
            cout << "*";
        }
        cout << "*\n";
    }
}

void rightAngledRight(int n){
    int i,j,k;
    for (i=0;i<n;i++){
        for (j=0; j<n-i; j++){
            cout << " ";
        }
        for (k=0; k<i;k++){
            cout << "*";
        }
        cout << "*\n";
    }
}

int main(){
    int n;
    cout << "Number of rows: ";
    cin >> n;
    rightAngledRight(n);
    return 0;
}