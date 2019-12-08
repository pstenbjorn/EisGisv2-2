def list_to_dict(alist):
    l = len(alist[0])
    k = alist[0]
    d = []
    del alist[0]
    for it in alist:
        i = 0
        dd = {}
        while i < l:
            dd[k[i]] = it[i]
            i += 1
    
        d.append(dd)
    
    return d
    