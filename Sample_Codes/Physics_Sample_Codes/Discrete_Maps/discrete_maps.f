c
c Discrete Maps
c        - Iteration of discrete map, not ODE integration
c Fortran version written by H. Nakanishi
c
      program iteration
      implicit real*8 (a-h,o-z)
      character ans,yes
      character*12 of
      yes='y'
10    call initialize(x0,map,a,b,c,iter,of)
      open(1,file=of,status='unknown')
      x=x0
      iter1=iter+1
      if(map.eq.1) then
          do 20 i=1,iter1
              write(1,15) dble(i-1),x
              x=f(x,b)
20        continue
      elseif(map.eq.2) then
          do 30 i=1,iter1
              write(1,15) dble(i-1),x
              x=g(x,a)
30        continue
      else
          do 40 i=1,iter1
              write(1,15) dble(i-1),x
              x=h(x,c)
40        continue
      endif
15    format(1x,1p,e12.5,2x,e12.5)
      close(1)
      print *,'another try ?'
      read(5,25) ans
25    format(a1)
      if(ans.eq.yes) go to 10
      stop
      end
c
c
c
      subroutine initialize(x0,map,a,b,c,iter,of)
      implicit real*8 (a-h,o-z)
      character*12 of
      print *,'which map? logistic (1), cusp (2), 4th order (3)?'
      read(5,*) map
      if(map.eq.1) then
          print *,'b in f(x)=4bx(1-x) ?'
          read(5,*) b
      elseif(map.eq.2) then
          print *,'a in g(x)=a(1-2|x-1/2|) ?'
          read(5,*) a
      else
          print *,'c in h(x)=c[1-(2x-1)**4] ?'
          read(5,*) c
      endif
      print *,'initial x ?'
      read(5,*) x0
      print *,'how may iterations?'
      read(5,*) iter
      print *,'output file?'
      read(5,15) of
15    format(a12)
      return
      end
c
c
c
      function f(x,b)
      implicit real*8 (a-h,o-z)
      f=4.d0*b*x*(1.d0-x)
      return
      end
c
      function g(x,a)
      implicit real*8 (a-h,o-z)
      g=a*(1.d0-2.d0*dabs(x-0.5d0))
      return
      end
c
      function h(x,c)
      implicit real*8 (a-h,o-z)
      h=c*(1.d0-(2.d0*x-1.d0)**4)
      return
      end