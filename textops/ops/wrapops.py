from textops import TextOp, WrapOpIter, WrapOpYield

class dosort(WrapOpYield): fn=sorted
class getmax(WrapOpIter): fn=max
class getmin(WrapOpIter): fn=min
class alltrue(WrapOpIter): fn=all
class anytrue(WrapOpIter): fn=any
class linenbr(WrapOpIter): fn=enumerate