function read_data

% Opciones
coeffs_surr=3;
plot_figures=1;
degree_plot=2;


% values
reynolds_data=10000:10000:20000000;
angles_data=-15:0.1:15;

% Lectura de valores para crear interpolacion
if coeffs_surr==2

    % lectura de los valores
    %InputPath=strcat('./',filesep,'INPUT',filesep,'results_Coefs_Reynolds',filesep);
    InputPath=strcat('./',filesep);

    
    % matriz coefficients
    num_reynolds=length(reynolds_data); % 2000;
    num_angles=length(angles_data); % 301;
    Cl_data=zeros(num_angles,num_reynolds);
    Cd_data=zeros(num_angles,num_reynolds);
    Cm_data=zeros(num_angles,num_reynolds);
    
    i_n_Re=0;
    for i_Re=reynolds_data
        i_n_Re=i_n_Re+1;
        % i_Re=38?0000;
        
        % i_re_read=readtable(strcat(InputPath,'Re_',num2str(i_Re),'.csv'));
        i_re_read=readtable(strcat(InputPath,'Re_',num2str(i_Re),'.csv'));
        
        % leer coolumnas
        i_re_angles=i_re_read{:,1};
        i_re_Cl=i_re_read{:,2};
        i_re_Cd=i_re_read{:,3};
        i_re_Cm=i_re_read{:,4};
        
        % interpolar a los valores dados
        i_re_Cl_interpol=interp1(i_re_angles,i_re_Cl,angles_data,'linear','extrap');
        i_re_Cd_interpol=interp1(i_re_angles,i_re_Cd,angles_data,'linear','extrap');
        i_re_Cm_interpol=interp1(i_re_angles,i_re_Cm,angles_data,'linear','extrap');
        
        % guardar variable
        Cl_data(:,i_n_Re)=i_re_Cl_interpol;
        Cd_data(:,i_n_Re)=i_re_Cd_interpol;
        Cm_data(:,i_n_Re)=i_re_Cm_interpol;

    end
    
    % guarda en un unico archivo para iterar aqui. y poner otra opcion.
    save('coefficients.mat','angles_data','Cl_data','Cd_data','Cm_data');

elseif coeffs_surr==3
    load('coefficients.mat');
end


% Plot
if plot_figures==1
    %find in list
    pos_angle=find(angles_data==degree_plot);

    % CL
    fig1 = figure(1);
    plot(reynolds_data,Cl_data(pos_angle,:))
    semilogx(reynolds_data,Cl_data(pos_angle,:));
    xlabel('Re'); ylabel('C_L');
    saveas(gcf,strcat('Cl_angle',num2str(degree_plot),'.png'))

    % CD
    fig2 = figure(2);
    plot(reynolds_data,Cd_data(pos_angle,:))
    semilogx(reynolds_data,Cd_data(pos_angle,:));
    xlabel('Re'); ylabel('C_D');
    saveas(gcf,strcat('Cd_angle',num2str(degree_plot),'.png'))

    % CM
    fig3 = figure(3);
    plot(reynolds_data,Cm_data(pos_angle,:))
    semilogx(reynolds_data,Cm_data(pos_angle,:));
    xlabel('Re'); ylabel('C_M');
    saveas(gcf,strcat('Cm_angle',num2str(degree_plot),'.png'))
end


end