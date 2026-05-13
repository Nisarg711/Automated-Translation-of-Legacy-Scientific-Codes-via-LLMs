c
c Simulation of radioactive decay - Euler or Runge-Kutta (2nd or 4th)
c Program to accompany "Computational Physics" by N. Giordano and H. Nakanishi
c Fortran version written by H. Nakanishi, need to be compiled with "-lpepl".
c
	program decay
c
c       Declare the arrays we will need
c
	dimension uranium(1003), t(1003)
c
c       Use subroutines to do the work
c
	call initialize(uranium,t,tau,dt,n,lsym,nsym,method)   
	call calculate(uranium,t,dt,tau,n,method)
	call display(uranium,t,tau,dt,n,lsym,nsym,method)
	stop
	end
c
	subroutine initialize(unuclei,t,tc,dt,n,lsym,nsym,method)      
c
c       Initialize variables
c
	dimension unuclei(1),t(1)
	character ans,yes
	yes='y'
	print *,'Euler (1), Runge-Kutta 2nd order (2), 4th (3) ? -> '
	read(5,*) method
	if(method.ne.1.and.method.ne.2.and.method.ne.3) then
		print *,'must select 1, 2 or 3 ..'
		stop
	endif
	print *,'initial number of nuclei -> '
	read(5,*) unuclei(1)
	t(1) = 0
	print *,'time constant -> '
	read(5,*) tc
	print *,'time step -> '
	read(5,*) dt 
	print *,'total time -> '
	read(5,*) time
	n=min(int(time/dt),1000)
	print *,'set line, symbol?'
	read(5,14) ans
14	format(a1)
	if(ans.eq.yes) then
		print *,'line and symbol numbers -> '
		read(5,*) lsym,nsym
	else
		lsym=-1
		nsym=1
	endif
	return
	end
c
	subroutine calculate(x,t,dt,tau,n,method)
c
c       Now use the Euler method or the Runge-Kutta (2nd or 4th order)
c
	dimension x(1),t(1)
	if(method.eq.1) then
		do 10 i = 1,n-1
		x(i+1)=x(i)-x(i)/tau*dt
		t(i+1) = t(i) + dt
10		continue
	elseif(method.eq.2) then
		do 30 i = 1,n-1
		dx=-x(i)/tau
		x1=x(i)+0.5*dt*dx
		dx2=-x1/tau
	    	x(i+1)=x(i)+dt*dx2
		t(i+1) = t(i) + dt
30		continue
	else
		do 40 i = 1,n-1
		dx=-x(i)/tau
		x1=x(i)+0.5*dt*dx
		dx2=-x1/tau
		x2=x(i)+0.5*dt*dx2
		dx3=-x2/tau
		x3=x(i)+dt*dx3
		dx4=-x3/tau
		x(i+1)=x(i)+0.16666667*dt*(dx+2*dx2+2*dx3+dx4)
		t(i+1) = t(i) + dt
40		continue
	endif
	return
	end
c
	subroutine display(uranium,t,tau,dt,n,lsym,nsym,method)
c
c       First set up title and label axes for graph. Plotting is a lot
c       of work in fortran.
c       This version displays output as well as writes to a file "graph.out".
c
	dimension uranium(1),t(1)
	call usrmon(.true.,.false.,-0.5,9.,-0.5,12.)
	call pltlun(19,.true.,.false.)
	call pltlfn('graph.out')
	call plots
	call plot(0.,3.5,-3)
	if(method.eq.1) then
	call text(0.2,5.8,0.2,'Radioactive Decay: Euler',0.,24,0)
	elseif(method.eq.2) then
	call text(0.2,5.8,0.2,'Radioactive Decay: Runge-Kutta2',0.,31,0)
	else
	call text(0.2,5.8,0.2,'Radioactive Decay: Runge-Kutta4',0.,31,0)
	endif
	call text(0.2,5.5,0.2,'Number of nuclei versus time',0.,28,0)
	call scalex(t,5.,n,1)
	call axctl(0.15,0.04,0.15,0.2,0.2,-1)
	call axisx(0.,0.,'Time(s)',-7,5.,0.,
     c	t(n+1),t(n+2),t(n+3),4)
	call axisx(0.,5.,' ',1,5.,0.,
     c	t(n+1),t(n+2),t(n+3),20)
	call scalex(uranium,5.,n,1)
	call axctl(0.15,0.04,0.15,0.2,0.2,-1)
	call axisx(0.,0.,'Number of Nuclei',16,5.,90.,
     c	uranium(n+1),uranium(n+2),uranium(n+3),-5)
	call axisx(5.,0.,' ',-1,5.,90.,
     c	uranium(n+1),uranium(n+2),uranium(n+3),-21)
	call line(t,uranium,n,1,lsym,nsym)
	call number(2.,3.5,0.2,tau,0.,'''tau = '',f5.2')
	call number(2.,4.0,0.2,dt,0.,'''dt = '',f5.2')
	call plot(0.,0.,999)
	return
	end
