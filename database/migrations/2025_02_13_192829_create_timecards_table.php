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
        Schema::create('timecards', function (Blueprint $table) {
            $table->engine = 'InnoDB';
            $table->charset = 'utf8mb4';
            $table->collation = 'utf8mb4_unicode_ci';
            $table->id();
            $table->unsignedBigInteger('employeeid');
            $table->date('workdate');
            $table->datetime('clockintime');
            $table->datetime('clockouttime');
            $table->datetime('break1begintime');
            $table->datetime('break1endtime');
            $table->integer('totalworkminutes');
            $table->unsignedBigInteger('branchid');
            $table->timestamps();
            $table->foreign('employeeid')->references('id')->on('employeefiles')->onDelete('cascade');
            $table->foreign('branchid')->references('id')->on('branch')->onDelete('cascade');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('timecards');
    }
};
