class application_service {

  require python_service

  $application_path = '/opt/application'
  $virtualenv_prefix = '/home/environments'

  $fcgi_options = 'maxrequests=1000 maxchildren=100 minspare=30 maxspare=45'

  file { $application_path:
    ensure  => directory,
    recurse => true,
    source  => 'puppet:///modules/application_service/application',
  }

  file { $virtualenv_prefix:
    ensure => directory,
    owner  => 'vagrant',
    group  => 'vagrant',
  }

  package { 'g++':
    ensure => present,
  }

  class p2d14 {

    $environment_name = 'p2d14'
    $python = 'python'
    $django_version = '1.4.8'
    $port = 9001

    $virtualenv_path = "${application_service::virtualenv_prefix}/${environment_name}"

    exec { "create_python_virtualenv_${environment_name}":
      command   => "/usr/bin/virtualenv --python=${python} ${virtualenv_path}",
      creates   => $virtualenv_path,
      user      => 'vagrant',
      logoutput => 'on_failure',
      require   => File["${application_service::virtualenv_prefix}"],
    }
    exec { "install_requirements_${environment_name}":
      command   => "${virtualenv_path}/bin/pip install Django==${django_version} flup",
      user      => 'vagrant',
      logoutput => 'on_failure',
      require   => Exec["create_python_virtualenv_${environment_name}"],
    }
    exec { "install_alpaca_django_${environment_name}":
      command   => "${virtualenv_path}/bin/python /vagrant/setup.py develop",
      timeout   => 3600,
      user      => 'vagrant',
      cwd       => '/vagrant',
      logoutput => 'on_failure',
      require   => [
        Exec["create_python_virtualenv_${environment_name}"],
        Package['g++'],
      ],
    }

    supervisor::service { $environment_name:
      ensure          => present,
      command         => "${virtualenv_path}/bin/python -u ${application_service::application_path}/manage.py runfcgi daemonize=false ${application_service::fcgi_options} host=127.0.0.1 port=${port}",
      environment     => "ALPACA_ENVIRONMENT=\"${environment_name}\"",
      user            => 'vagrant',
      startsecs       => 5,
      stopasgroup     => true,
      redirect_stderr => true,
      require         => [
        Exec["install_requirements_${environment_name}"],
        Exec["install_alpaca_django_${environment_name}"],
      ],
    }

  }

  include p2d14

}
