c
c Simulation of radioactive decay - Euler or Runge-Kutta (2nd or 4th)
c Program to accompany "Computational Physics" by N. Giordano and H. Nakanishi
c Fortran version written by H. Nakanishi
c Modified: Removed external plotting library dependency, prints array values instead
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
	dimension unuclei(*),t(*)
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
	dimension x(*),t(*)
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
c       Display results: Print time and uranium values to compare
c       No external plotting library dependency
c
	dimension uranium(*),t(*)
	character methodname*20
	
	if(method.eq.1) then
		methodname = 'Euler'
	elseif(method.eq.2) then
		methodname = 'Runge-Kutta2'
	else
		methodname = 'Runge-Kutta4'
	endif
	
	print *,'='
	print *,'Radioactive Decay: ',methodname
	print *,'tau = ',tau
	print *,'dt = ',dt
	print *,'='
	print *,'Time (s) | Number of Nuclei'
	print *,'-'
	
	do 50 i = 1,n,max(1,n/20)
		print 100, t(i), uranium(i)
50	continue
	
100	format(f10.4,' | ',f15.2)
	
	return
	end
