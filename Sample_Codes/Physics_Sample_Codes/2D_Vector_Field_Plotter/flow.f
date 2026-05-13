c
c Plotting of arrows from a vector field data file
c
c Fortran version written by H. Nakanishi
c
      program flow
c
c
c
      character*12 if
      dimension x(10000),y(10000),z1(10000),z2(10000),r(10000)
c
c       Use subroutines to do the work
c
      call init(if,rmin,afac,aoff,xmin,xmax,ymin,ymax,x,y,z1,z2,r,n)
      call disp(if,rmin,afac,aoff,xmin,xmax,ymin,ymax,x,y,z1,z2,r,n)
      stop
      end
c
      subroutine init(if,rmin,afac,aoff,xmin,xmax,ymin,ymax
     c		,x,y,z1,z2,r,n)
c
c       Initialize variables
c
      character*12 if
      dimension x(1),y(1),z1(1),z2(1),r(1)
      print *,'Flow: input file name ?'
      read(5,15) if
15    format(a12)
      open(1,file=if,status='old')
      rewind(1)
      rmin=0.
      rmax=0.
      n=0
      do 10 i=1,10000
      read(1,*,end=20) x(i),y(i),z1(i),z2(i)
      if(i.eq.1) then
          xmin=x(i)
          xmax=x(i)
          ymin=y(i)
          ymax=y(i)
      endif
      n=n+1
      r(i)=sqrt(z1(i)**2+z2(i)**2)
      if(r(i).lt.rmin) rmin=r(i)
      if(r(i).gt.rmax) rmax=r(i)
      if(x(i).lt.xmin) xmin=x(i)
      if(x(i).gt.xmax) xmax=x(i)
      if(y(i).lt.ymin) ymin=y(i)
      if(y(i).gt.ymax) ymax=y(i)
10    continue
20    close(1)
      print *,'max vector length = ',rmax,', min = ',rmin
      if(rmax.ne.rmin) then
          print *,'map the max and min lengths to: '
          read(5,*) amax,amin
          afac=(amax-amin)/(rmax-rmin)
          aoff=amin
      else
          print *,'map the arrow length to: '
          read(5,*) amin
          afac=0.
          aoff=amin
      endif
      return
      end
c
      subroutine disp(if,rmin,afac,aoff,xmin,xmax,ymin,ymax
     c		,x,y,z1,z2,r,n)
c
c
c
      character*12 if
      dimension x(1),y(1),z1(1),z2(1),r(1)
      
      if(xmin.ne.xmax) then
          xfac=5./(xmax-xmin)
          xoff=0.
      else
          xfac=1.
          xoff=2.5
      endif
      if(ymin.ne.ymax) then
          yfac=5./(ymax-ymin)
          yoff=0.
      else
          yfac=0.
          yoff=2.5
      endif
      
      open(unit=19, file='graph.out', status='unknown')
      write(19, *) '      x0            y0            a0            th'
      do 10 i=1,n
          x0=xfac*(x(i)-xmin)+xoff
          y0=yfac*(y(i)-ymin)+yoff
          r0=sqrt(z1(i)**2+z2(i)**2)
          a0=afac*(r0-rmin)+aoff
          if(z1(i).ne.0) then
              th=atan(z2(i)/z1(i))*180./3.14159
          else
              th=90.
              if(z2(i).lt.0) th=270.
          endif
          if(z1(i).lt.0) th=th+180.
          if(th.lt.0) th=th+360.
          write(19, *) x0, y0, a0, th
10    continue
      close(19)
      
      print *, 'Data successfully written to graph.out for comparison.'
      return
      end