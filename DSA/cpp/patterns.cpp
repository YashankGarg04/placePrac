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

void hollowDiamond(int n){
    int i,j,k;
    for (i=0;i<n;i++){
        for (j=0; j<n-i-1; j++){
            cout << " ";
        }
        for (k=0; k<(2*i+1);k++){
            if(k==0 || k==2*i){
                cout << "*";
            }
            else{
                cout << " ";
            }
        }
        cout << "\n";
    }

    for (i=n-1;i>0;i--){
        for (j=0; j<n-i; j++){
            cout << " ";
        }
        for (k=0; k<(2*i-1);k++){
            if(k==0 || k==(2*i-2)){
                cout << "*";
            }
            else{
                cout << " ";
            }
        }
        cout << "\n";
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

void pyramid(int n){
    int i,j,k;
    for (i=0;i<n;i++){
        for (j=0; j<n-i-1; j++){
            cout << " ";
        }
        for (k=0; k<(2*i+1);k++){
            cout << "*";
        }
        cout << "\n";
    }
}

void invertedPyramid(int n){
    int i,j,k;
    for (i=n;i>0;i--){
        for (j=0; j<n-i; j++){
            cout << " ";
        }
        for (k=0; k<(2*i-1);k++){
            cout << "*";
        }
        cout << "\n";
    }
}

int main(){
    int n;
    cout << "Number of rows: ";
    cin >> n;
    hollowDiamond(n);
    return 0;
}