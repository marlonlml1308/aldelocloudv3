<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {

        Schema::create('employeefiles', function (Blueprint $table) {
            $table->engine = 'InnoDB';
            $table->charset = 'utf8mb4';
            $table->collation = 'utf8mb4_unicode_ci';
            $table->id();
            $table->string('firstname');
            $table->string('lastname');
            $table->unsignedBigInteger('jobtitleid');
            $table->string('securitylevel');
            $table->string('socialsecuritynumber');
            $table->string('accesscode')->unique()->nullable();
            $table->boolean('employeeinactive',false);
            $table->timestamps();
            $table->foreign('jobtitleid')->references('id')->on('jobtitles')->onDelete('cascade');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('employees');
    }
};
