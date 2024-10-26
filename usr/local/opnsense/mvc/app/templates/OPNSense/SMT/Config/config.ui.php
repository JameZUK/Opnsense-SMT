<?php

/** @var $this \OPNSense\SMT\View\config */

use OPNSense\SMT\SMT;
use OPNSense\SMT\SMTController;

?>

<section class="page-content">
    <div class="container-fluid">
        <form action="/smts/config/save" method="post">
            <div class="card">
                <header class="card-heading">
                    <h3 class="card-title">SMT Plugin Configuration</h3>
                </header>
                <div class="card-body">
                    <div class="form-group">
                        <label for="unbound_reload_command">Unbound Reload Command</label>
                        <input type="text" class="form-control" id="unbound_reload_command" name="unbound_reload_command" value="<?=htmlspecialchars($this->config->opnsense->unbound_reload_command)?>" required>
                        <small class="form-text text-muted">Command to reload Unbound DNS, e.g., "sudo service unbound reload"</small>
                    </div>
                    <div class="form-group">
                        <label for="blocklist_repo_url">Blocklist Repository URL</label>
                        <input type="url" class="form-control" id="blocklist_repo_url" name="blocklist_repo_url" value="<?=htmlspecialchars($this->config->blocklist->repo_url)?>" required>
                    </div>
                    <div class="form-group">
                        <label for="blocklist_local_path">Local Blocklist Path</label>
                        <input type="text" class="form-control" id="blocklist_local_path" name="blocklist_local_path" value="<?=htmlspecialchars($this->config->blocklist->local_path)?>" required>
                    </div>
                    <div class="form-group">
                        <label for="usage_threshold_hours">Usage Threshold (Hours)</label>
                        <input type="number" class="form-control" id="usage_threshold_hours" name="usage_threshold_hours" value="<?=htmlspecialchars($this->config->social_media->usage_threshold_hours)?>" min="1" required>
                    </div>
                    <div class="form-group">
                        <label for="block_duration_minutes">Block Duration (Minutes)</label>
                        <input type="number" class="form-control" id="block_duration_minutes" name="block_duration_minutes" value="<?=htmlspecialchars($this->config->social_media->block_duration_minutes)?>" min="1" required>
                    </div>
                    <div class="form-group">
                        <label for="unbound_log_file">Unbound Log File Path</label>
                        <input type="text" class="form-control" id="unbound_log_file" name="unbound_log_file" value="<?=htmlspecialchars($this->config->unbound->log_file)?>" required>
                    </div>
                    <div class="form-group">
                        <label for="rpz_file">RPZ File Path</label>
                        <input type="text" class="form-control" id="rpz_file" name="rpz_file" value="<?=htmlspecialchars($this->config->unbound->rpz_file)?>" required>
                    </div>
                    <div class="form-group">
                        <label for="logging_level">Logging Level</label>
                        <select class="form-control" id="logging_level" name="logging_level" required>
                            <?php
                            $levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'];
                            foreach ($levels as $level) {
                                $selected = ($this->config->logging->level == $level) ? 'selected' : '';
                                echo "<option value=\"$level\" $selected>$level</option>";
                            }
                            ?>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="logging_file">Logging File Path</label>
                        <input type="text" class="form-control" id="logging_file" name="logging_file" value="<?=htmlspecialchars($this->config->logging->file)?>" required>
                    </div>
                    <div class="form-group">
                        <div class="custom-control custom-switch">
                            <input type="checkbox" class="custom-control-input" id="enable_service" name="enable_service" <?= ($this->config->opnsense->enable_service == 'yes') ? 'checked' : '' ?>>
                            <label class="custom-control-label" for="enable_service">Enable SMT Service</label>
                        </div>
                    </div>
                </div>
                <footer class="card-footer">
                    <button type="submit" class="btn btn-primary">Save Configuration</button>
                </footer>
            </div>
        </form>
    </div>
</section>

