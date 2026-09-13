# CPP
### Ternary or Conditional Operators
Conditional operator returns the value, based on the condition. This operator takes three operands, therefore it is known as a Ternary Operator.
#### Syntax:
```Expression1 ? Expression2 : Expression3```
In the above statement:

- The ternary operator ? determines the answer on the basis of the evaluation of Expression1.
- If Expression1 is true, then Expression2 gets evaluated.
- If Expression1 is false, then Expression3 gets evaluated.
```
#include <iostream>
using namespace std;

int main() {
    int a = 3, b = 4;

    // Conditional Operator
    int result = (a < b) ? b : a;
    cout << "The greatest number "
          "is " << result;

    return 0;
}
```
### Miscellaneous Operators
#### sizeof Operator
sizeof operator is a unary operator used to compute the size of its operand or variable in bytes. For example,
```
sizeof (char);
sizeof (var_name);
```
#### Comma Operator (,)
Comma operator is a binary operator that is used for multiple purposes. It is used as a separator or used to evaluate its first operand and discards the result; it then evaluates the second operand and returns this value (and type).
```
int n = (m+1, m-2, m+5);
int a, b, c;
```
#### Addressof Operator (&)
Addressof operator is used to find the memory address in which a particular variable is stored. In C++, it is also used to create a reference.
```&var_name;```
#### Dot Operator(.)
Dot operator is used to access members of structure variables or class objects using their object names
```obj . member;```
#### Arrow Operator
Arrow operator is used to access the variables of classes or structures through its pointer.
```
sptr -> member;
```
#### Casting Operators
Casting operators are used to convert the value of one data type to another data type. For example, for an integer value x:
```
(float)x
static_cast<float>(x)
```
### Input/Output
#### Standard Input Stream - cin
```
#include <iostream>
using namespace std;

int main()
{
    int age;
    // Taking input from user and store it in variable
    cin >> age;
    
    // Output the entered age
    cout << "Age entered: " << age;
    return 0;
}
```
#### Un-buffered Standard Error Stream - cerr
- cerr is the standard error stream used to display error messages. It is an instance of the ostream class.
- It is an unbuffered output stream used to display error or warning messages immediately, ensuring they appear instantly without any buffering delays like cout
```
#include <iostream>
using namespace std;

int main()
{
    cerr << "An error occurred";
    return 0;
}
```
#### Buffered Standard Error Stream - clog
- clog is the standard logging stream used to display error or log messages. It is an instance of the ostream class, like cerr.
- Messages are first stored in a buffer and displayed only when the buffer is full or explicitly flushed using flush() (Buffered output)
- Useful for logging messages that don’t need to appear immediately on the screen.
- Unlike cerr, output from clog may be delayed due to buffering
```
#include <iostream>
using namespace std;

int main()
{
    clog << "An error occurred";
    return 0;
}
```