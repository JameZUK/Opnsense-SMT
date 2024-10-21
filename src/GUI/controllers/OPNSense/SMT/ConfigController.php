<?php

namespace OPNSense\SMT;

use OPNSense\Base\IndexController;
use OPNSense\Core\Backend;

class ConfigController extends IndexController
{
    public function indexAction()
    {
        $this->view->pick('OPNSense/SMT/Config/config.ui');
    }

    public function saveAction()
    {
        if ($this->request->isPost()) {
            $post = $this->request->getPost();
            $model = Config::getInstance();

            // Update configuration
            $model->opnsense->unbound_reload_command = $post['unbound_reload_command'];
            $model->blocklist->repo_url = $post['blocklist_repo_url'];
            $model->blocklist->local_path = $post['blocklist_local_path'];
            $model->social_media->usage_threshold_hours = $post['usage_threshold_hours'];
            $model->social_media->block_duration_minutes = $post['block_duration_minutes'];
            $model->unbound->log_file = $post['unbound_log_file'];
            $model->unbound->rpz_file = $post['rpz_file'];
            $model->logging->level = $post['logging_level'];
            $model->logging->file = $post['logging_file'];
            $model->opnsense->enable_service = isset($post['enable_service']) ? 'yes' : 'no';

            // Save the configuration
            $model->serializeToConfig();

            // Generate config.yaml for the Python script
            $config_yaml = [
                'opnsense' => [
                    'unbound_reload_command' => (string)$model->opnsense->unbound_reload_command
                ],
                'blocklist' => [
                    'repo_url' => (string)$model->blocklist->repo_url,
                    'local_path' => (string)$model->blocklist->local_path
                ],
                'social_media' => [
                    'usage_threshold_hours' => (int)$model->social_media->usage_threshold_hours,
                    'block_duration_minutes' => (int)$model->social_media->block_duration_minutes
                ],
                'logging' => [
                    'level' => (string)$model->logging->level,
                    'file' => (string)$model->logging->file
                ],
                'unbound' => [
                    'log_file' => (string)$model->unbound->log_file,
                    'rpz_file' => (string)$model->unbound->rpz_file
                ]
            ];

            // Use PHP's YAML extension or a library like Symfony YAML
            // Ensure the YAML library is installed and included
            // Here, we assume the Symfony YAML component is available
            // If not, you'll need to install it or use an alternative method
            require_once 'vendor/autoload.php';
            use Symfony\Component\Yaml\Yaml;

            try {
                $yaml_content = Yaml::dump($config_yaml, 4, 2);
                file_put_contents('/usr/local/opnsense/mvc/app/plugins/smt/etc/opnsense/scripts/smt/config.yaml', $yaml_content);
            } catch (\Exception $e) {
                $this->session->setFlash('error', 'Failed to generate config.yaml: ' . $e->getMessage());
                return $this->response->redirect('/smts/config');
            }

            // Handle service start/stop
            $enable_service = ($model->opnsense->enable_service == 'yes');
            $backend = new Backend();
            if ($enable_service) {
                $backend->configdRun("service smt start");
            } else {
                $backend->configdRun("service smt stop");
            }

            $this->session->setFlash('success', 'Configuration saved and service status updated.');
        }

        return $this->response->redirect('/smts/config');
    }
}

