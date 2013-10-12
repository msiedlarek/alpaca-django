class nginx_service {

  package { 'nginx':
    ensure => present,
  }

  file { '/etc/nginx/sites-enabled/default':
    ensure  => absent,
    notify  => Service['nginx'],
    require => Package['nginx'],
  }

  file { '/etc/nginx/sites-available/application':
    ensure  => file,
    content => template('nginx_service/application.erb'),
    notify  => Service['nginx'],
    require => Package['nginx'],
  }
  file { '/etc/nginx/sites-enabled/application':
    ensure  => link,
    target  => '/etc/nginx/sites-available/application',
    notify  => Service['nginx'],
    require => [
      Package['nginx'],
      File['/etc/nginx/sites-available/application'],
    ],
  }

  service { 'nginx':
    ensure  => running,
    require => Package['nginx'],
  }

}
